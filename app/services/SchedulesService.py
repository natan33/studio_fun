from sqlalchemy import or_
from app import db

from app.utils.api_response import ApiResponse


class SchedulesService:
    def __init__(self,formrs=None,request=None):
        self.formrs = formrs
        self.request = request

    def edit_schedule(self):
        """Metodo para editar uma turma. 
        pelo ID fornecido no formulário."""
        try:
            from app.models.pages.academy import ClassSchedule
            from app.controllers.forms.academy_forms import ScheduleForm

            form = self.formrs or ScheduleForm(self.request.form)

            schedule_id = self.request.form.get('schedule_id')

            if schedule_id: # MODO EDIÇÃO
                schedule = ClassSchedule.query.get(schedule_id)
                if not schedule:
                    return ApiResponse.error(message="Turma não encontrada")
            
                if form.validate_on_submit():
                    schedule.activity_id = form.activity_id.data
                    schedule.day_of_week = form.day_of_week.data
                    schedule.start_time = form.start_time.data
                    schedule.max_capacity = form.max_capacity.data
                    
                    schedule.save() # Seu método save() do model
                    
                    return ApiResponse.success(message="Turma atualizada com sucesso!" if schedule_id else "Turma criada!")
            
            return ApiResponse.error(message="Erro na validação do formulário")
        except Exception as e:
            db.session.rollback()
            print(e)
            return ApiResponse.error(message=str(e))

    def list_schedules(self):
            
        """Metodo para listar todas as turmas cadastradas."""
        try:
            from app.models.pages.academy import ClassSchedule, Activity
            
            # Buscamos todas as turmas
            schedules = ClassSchedule.query.join(Activity).filter(
                or_(
                    ClassSchedule.is_active == True,
                    ClassSchedule.is_active == None
                )
            ).order_by(
                ClassSchedule.day_of_week, 
                ClassSchedule.start_time
            ).all()   
            
            # Formatamos os dados para JSON
            data = [{
                "id": s.id,
                "activity": s.activity_ref.name,
                "day": s.day_of_week,
                "time": s.start_time.strftime('%H:%M'),
                "capacity": s.max_capacity,
                "current_enrolled": (count := len([e for e in s.enrolled_students if e.status == 'Ativo'])),
                "percent": int((count / s.max_capacity) * 100) if s.max_capacity > 0 else 0
            } for s in schedules]
            data_sorted = sorted(data, key=lambda x: x['percent'], reverse=True)

            return ApiResponse.success(data=data_sorted)
        except Exception as e:
                db.session.rollback()
                print(e)
                return ApiResponse.error(message=str(e))
    
    def list_schedule_students(self, id=None):
        """Metodo para listar os alunos matriculados em uma turma específica."""
        try:
            from app.models.pages.academy import ClassSchedule
            schedule = ClassSchedule.query.get_or_404(id)
            if not schedule:
                return ApiResponse.error(message="Turma não encontrada.")
            # Buscamos as matrículas ativas
            students_data = [{
                "id": e.student.id,
                "name": e.student.full_name,
                "status": e.status
            } for e in schedule.enrolled_students if e.status == 'Ativo']
            
            return ApiResponse.success(data={
                "activity": schedule.activity_ref.name,
                "day": schedule.day_of_week,
                "time": schedule.start_time.strftime('%H:%M'),
                "students": students_data
            })
        except Exception as e:
                db.session.rollback()
                print(e)
                return ApiResponse.error(message=str(e))


    def delete_schedule(self, id=None):
        """Metodo para deletar um horário específico pelo ID.
        de uma turma ativa ou inativa."""
        try:
            from app.models.pages.academy import ClassSchedule
            sch = ClassSchedule.query.get_or_404(id)
            if not sch:
                return ApiResponse.error(message="Turma não encontrada.")
            
            sch.is_active = False
            db.session.commit()
            return ApiResponse.success(message="Horário removido com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(e)
            return ApiResponse.error(message=str(e))
        
    def get_schedule_detail(self, id=None):
        """Metodo para obter os detalhes de uma turma específica pelo ID."""
        try:
            from app.models.pages.academy import ClassSchedule
        
            sch = ClassSchedule.query.get_or_404(id)
            
            return ApiResponse.success(data={
                "id": sch.id,
                "activity_id": sch.activity_id,
                "day_of_week": sch.day_of_week,
                "start_time": sch.start_time.strftime('%H:%M'),
                "max_capacity": sch.max_capacity
            })
        except Exception as e:
            db.session.rollback()
            print(e)
            return ApiResponse.error(message=str(e))