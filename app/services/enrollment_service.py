from sqlalchemy import or_
from app import db
from app.models import *
from app.utils.api_response import ApiResponse


class EnrollmentService:
    def __init__(self,forms=None,request=None):
        self.form = forms
        self.request=request

    def list_enrollments(self):
            try:
                from app.models.pages.academy import Enrollment
    
                # Buscamos todas as matrículas, incluindo as relações para evitar múltiplas queries
                enrollments = Enrollment.query.all()
                
                data = [{
                    "id": e.id,
                    "student_name": e.student.full_name,
                    "activity": e.schedule.activity_ref.name,
                    "day": e.schedule.day_of_week,
                    "time": e.schedule.start_time.strftime('%H:%M'),
                    "status": e.status,
                    "enrolled_at": e.enrollment_date.strftime('%d/%m/%Y')
                } for e in enrollments]
                
                # Ordenar pelas mais recentes primeiro
                data.sort(key=lambda x: x['id'], reverse=True)
    
                return ApiResponse.success(data=data)
            except Exception as e:
                print(f"Erro no Service: {e}")
                return ApiResponse.error(message=str(e))

    def get_enrollment_dashboard_data(self):
            try:
                from app.models.pages.academy import Enrollment, Attendance

                enrollments = Enrollment.query.all()
                
                # 1. Contagem por Status
                total = len(enrollments)
                ativos = len([e for e in enrollments if e.status == 'Ativo'])
                trancados = len([e for e in enrollments if e.status == 'Trancado'])

                # 2. Lógica de Frequência Média
                total_presencas = Attendance.query.count()
                freq_media = 0
                if total > 0 and total_presencas > 0:
                    freq_media = round((total_presencas / (total * 12)) * 100, 1)

                # O SEGREDO: Envie apenas os números (stats), não os objetos do banco
                data = {
                    "total": total,
                    "ativos": ativos,
                    "trancados": trancados,
                    "freq_media": f"{freq_media}%" if freq_media > 0 else "---"
                }
            
                return ApiResponse.success(data=data)
            except Exception as e:
                print(f"Erro no Service: {e}")
                return ApiResponse.error(message=str(e))
            
    def update_enrollment_status(self, enrollment_id=None, new_status=None):
            try:
                from app.models.pages.academy import Enrollment
                
                enrollment = Enrollment.query.get(enrollment_id)
                
                if not enrollment:
                    return ApiResponse.error(message="Matrícula não encontrada.")
                
                # Atualiza apenas o status
                enrollment.status = new_status
                db.session.commit()
                
                return ApiResponse.success(message=f"Matrícula alterada para {new_status}!")
                
            except Exception as e:
                db.session.rollback()
                print(e)
                return ApiResponse.error(message=str(e))
            
    def toggle_enrollment_status(self, enrollment_id=None, active_status="Ativo"):
            try:
                from app.models.pages.academy import Enrollment
                
                enrollment = Enrollment.query.get_or_404(enrollment_id)
                
                # Lógica de alternância (Toggle)
                if enrollment.status == active_status:
                    enrollment.status = 'Trancado'
                    message = "Matrícula trancada com sucesso!"
                else:
                    enrollment.status = active_status
                    message = "Matrícula reativada com sucesso!"
                    
                enrollment.save() # Assume que seu model tem o método .save()
                
                return ApiResponse.success(message=message, data={"new_status": enrollment.status})
                
            except Exception as e:
                db.session.rollback()
                return ApiResponse.error(message=f"Erro ao alterar status: {str(e)}")

    @staticmethod
    def delete_enrollment(enrollment_id=None):
        try:
            from app.models.pages.academy import Enrollment
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return False, "Matrícula não encontrada."

            db.session.delete(enrollment)
            db.session.commit()
            return True, "Matrícula excluída com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    def get_students(self):
        search_term = self.request.args.get('q', '')  # O Select2 envia o termo de busca no parâmetro 'q'
    
        # Filtra os alunos no banco de dados (exemplo com SQLAlchemy)
        students = Student.query.filter(Student.full_name.ilike(f'%{search_term}%')).limit(10).all()
        
        # Formata para o padrão que o Select2 entende
        results = [{"id": s.id, "text": s.full_name} for s in students]
        # Usando seu ApiResponse (exemplo de estrutura)
        return ApiResponse.success(data=results)
    
    def get_schedules(self):
        search = self.request.args.get('q', '')
    
        # Busca as turmas filtrando pelo nome da atividade (activity_ref)
        # Ajuste o filtro de acordo com seu banco (ex: Schedule.activity_ref.has...)
        query = ClassSchedule.query.join(Activity).filter(
            or_(
                ClassSchedule.is_active == True,
                ClassSchedule.is_active == None
            )
        )

        # Se o usuário digitar algo, filtra pelo nome da atividade ou dia da semana
        if search:
            query = query.filter(
                or_(
                    Activity.name.ilike(f'%{search}%'),
                    ClassSchedule.day_of_week.ilike(f'%{search}%')
                )
            )

        # Ordenação conforme sua necessidade
        schedules = query.order_by(
            ClassSchedule.day_of_week, 
            ClassSchedule.start_time
        ).all()
        
        # Formata para o Select2
        results = [
            {
                "id": sch.id, 
                "text": f"{sch.activity_ref.name} - {sch.day_of_week} às {sch.start_time.strftime('%H:%M')}"
            } 
            for sch in schedules
        ]
        
        return ApiResponse.success(data=results)