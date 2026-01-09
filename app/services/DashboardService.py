
from datetime import datetime
from app.models.pages.academy import  Activity, ClassSchedule, Enrollment
from app.models.pages.finance import Expense, Invoice
from app.models.pages.students import Student
from sqlalchemy import and_, extract, func, or_
from app import db
from app.utils.api_response import ApiResponse

class DashboardService:

    def get_main_stats(self):
        """Retorna os números globais para os cards do topo"""
        from sqlalchemy import or_

        # 1. Apenas contamos no banco (mais rápido que dar .all() e depois contar)
        count_active_schedules = ClassSchedule.query.filter(
            or_(
                ClassSchedule.is_active == True,
                ClassSchedule.is_active == None
            )
        ).count()

        return {
            'total_students': Student.query.count(),
            'total_enrollments': Enrollment.query.filter_by(status='Ativo').count(),
            'total_schedules': count_active_schedules
        }
    def get_schedules_occupancy(self):
        """Calcula a ocupação de cada turma com List Comprehension e ordena pelas mais cheias"""
        from sqlalchemy import or_
        
        # 1. Busca os horários ativos
        schedules = ClassSchedule.query.join(Activity).filter(
            or_(ClassSchedule.is_active == True, ClassSchedule.is_active == None)
        ).all()

        # 2. Gera a lista usando List Comprehension
        # Nota: Fazemos a contagem de matrículas dentro da compreensão
        stats = [
            {
                'label': f"{sch.activity_ref.name} ({sch.day_of_week})",
                'time': sch.start_time.strftime('%H:%M'),
                'current': (current := Enrollment.query.filter_by(schedule_id=sch.id, status='Ativo').count()),
                'max': sch.max_capacity,
                'pct': round((current / sch.max_capacity * 100), 1) if sch.max_capacity > 0 else 0
            } 
            for sch in schedules
        ]

        # 3. Ordena a lista: as maiores porcentagens ('pct') primeiro
        # reverse=True coloca o maior valor no topo
        sorted_stats = sorted(stats, key=lambda x: x['pct'], reverse=True)
        
        return sorted_stats[:5]

    def get_full_dashboard(self):
        """Consolida todos os dados para o controller"""
        return {
            'cards': self.get_main_stats(),
            
        }
    
    def get_tbl_dashboard(self):
        return  self.get_schedules_occupancy()
    
    @staticmethod
    def get_dashboard_cards():
        try:
            today = datetime.now()
            current_month = today.month
            current_year = today.year
            # 1. Total Recebido
            total_income = db.session.query(func.sum(Invoice.amount)).filter(
                and_(
                    Invoice.status == 'paid',
                    extract('month', Invoice.paid_at) == current_month,
                    extract('year', Invoice.paid_at) == current_year # SEMPRE filtre o ano também!
                )
            ).scalar() or 0

            # 2. Total Pago
            total_expense = db.session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.status == 'paid',
                    extract('month', Expense.payment_date) == current_month,
                    extract('year', Expense.payment_date) == current_year
                )
            ).scalar() or 0

            count_active_schedules = ClassSchedule.query.filter(
                or_(
                    ClassSchedule.is_active == True,
                    ClassSchedule.is_active == None
                )
            ).count()

            data = {
                "income": float(total_income),
                "expense": float(total_expense),
                "profit": float(total_income - total_expense),
                "margin": round(((total_income - total_expense) / total_income * 100), 2) if total_income > 0 else 0,
                'total_students': Student.query.count(),
                'total_enrollments': Enrollment.query.filter_by(status='Ativo').count(),
                'total_schedules': count_active_schedules
            }
            print(data)
            return ApiResponse.success(data=data)
        except Exception as e:
            return ApiResponse.error(str(e))