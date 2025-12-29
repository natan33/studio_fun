
from app.models.pages.academy import  ClassSchedule, Enrollment
from app.models.pages.students import Student
from sqlalchemy import func

class DashboardService:

    def get_main_stats(self):
        """Retorna os números globais para os cards do topo"""
        return {
            'total_students': Student.query.count(),
            'total_enrollments': Enrollment.query.filter_by(status='Ativo').count(),
            'total_schedules': ClassSchedule.query.count()
        }

    def get_schedules_occupancy(self):
        """Calcula a ocupação de cada turma para as barras de progresso"""
        schedules = ClassSchedule.query.all()
        stats = []

        for sch in schedules:
            # Contagem de alunos matriculados nesta turma
            current_enrolled = Enrollment.query.filter_by(schedule_id=sch.id, status='Ativo').count()
            
            # Cálculo de porcentagem de lotação
            occupancy_pct = (current_enrolled / sch.max_capacity * 100) if sch.max_capacity > 0 else 0
            
            stats.append({
                'label': f"{sch.activity_ref.name} ({sch.day_of_week})",
                'time': sch.start_time.strftime('%H:%M'),
                'current': current_enrolled,
                'max': sch.max_capacity,
                'pct': round(occupancy_pct, 1)
            })
            
        return stats

    def get_full_dashboard(self):
        """Consolida todos os dados para o controller"""
        return {
            'cards': self.get_main_stats(),
            'occupancy': self.get_schedules_occupancy()
        }