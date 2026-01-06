from datetime import datetime
from sqlalchemy import or_
from app import db
from app.models.pages.academy import Activity, ClassSchedule, Enrollment
from app.models.pages.core import WelcomeEmailLog
from app.models.pages.finance import Plan
from app.models.pages.students import Student
from app.utils.api_response import ApiResponse
import logging

logger = logging.getLogger(__name__)

class AcademyService:
    def __init__(self, form=None, request=None):
        self.form = form
        self.request = request

    def create_activity(self):
        """Cria um novo tipo de aula (Zumba, Funcional, etc)"""
        if not self.form or not self.form.validate_on_submit():
            errors = {field: err[0] for field, err in self.form.errors.items()}
            return ApiResponse.error(message="Erro de validação", data=errors)

        try:
            # Verifica se já existe uma atividade com esse nome
            name_upper = self.form.name.data.upper()
            exists = Activity.query.filter(Activity.name.ilike(name_upper)).first()
            if exists:
                return ApiResponse.error(message="Esta atividade já está cadastrada.")

            new_activity = Activity(
                name=self.form.name.data,
                description=self.form.description.data
            )
            db.session.add(new_activity)
            db.session.commit()
            
            logger.info(f"Nova atividade criada: {new_activity.name}")
            return ApiResponse.success(message="Tipo de aula cadastrado com sucesso!")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar atividade: {str(e)}")
            return ApiResponse.error(message="Erro interno ao salvar atividade.")

    
    
    def list_all(self, as_dict=False):
        """Retorna todos os alunos. Se as_dict for True, retorna para JSON."""
        students = Activity.query.order_by(Activity.name).all()
        
        if as_dict:
            return [s.to_dict() for s in students]
        
        return students # Retorna a lista de objetos para o Jinj # Exemplo se tiver to_dict


    def update_schedule(self):
        if not self.form or not self.form.validate_on_submit():
            return ApiResponse.error(message="Erro nos dados da turma.", data=self.form.errors)

        try:
            schedule_id = self.request.form.get('schedule_id')
            schedule = ClassSchedule.query.get(schedule_id)
            if not schedule:
                return ApiResponse.error(message="Horário de turma não encontrado.")

            schedule.activity_id = self.form.activity_id.data
            schedule.day_of_week = self.form.day_of_week.data
            schedule.start_time = self.form.start_time.data
            schedule.max_capacity = self.form.max_capacity.data

            db.session.commit()
            return ApiResponse.success(message="Horário de turma atualizado com sucesso!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(message=f"Erro ao atualizar horário: {str(e)}")

    def create_schedule(self):
        if not self.form or not self.form.validate_on_submit():
            return ApiResponse.error(message="Erro nos dados da turma.", data=self.form.errors)

        try:
            new_schedule = ClassSchedule(
                activity_id=self.form.activity_id.data, # Verifique se o nome aqui está correto
                day_of_week=self.form.day_of_week.data,
                start_time=self.form.start_time.data,
                max_capacity=self.form.max_capacity.data
            )
            new_schedule.save()
            return ApiResponse.success(message="Horário de turma criado com sucesso!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(message=f"Erro ao criar horário: {str(e)}")

    def list_schedules(self):
            """Retorna a lista de horários/turmas"""
            from app.models.pages.academy import ClassSchedule, Activity
            
            # Fazemos um join com Activity para poder mostrar o NOME da aula na tabela
            return ClassSchedule.query.join(Activity).filter(
                or_(
                    ClassSchedule.is_active == True,
                    ClassSchedule.is_active == None
                )
            ).order_by(
                ClassSchedule.day_of_week, 
                ClassSchedule.start_time
            ).all()
    
    def format_class_schedule(self,class_schedule=None):
        """
        Converte o day_of_week (0-6) e o start_time 
        em uma string amigável para o e-mail.
        """
        # Mapeamento do padrão 0-6 para nomes em português
        dias_semana = {
            '0': 'Segunda-feira',
            '1': 'Terça-feira',
            '2': 'Quarta-feira',
            '3': 'Quinta-feira',
            '4': 'Sexta-feira',
            '5': 'Sábado',
            '6': 'Domingo'
        }

        # Obtém o nome do dia através da string salva no banco
        dia_nome = dias_semana.get(str(class_schedule.day_of_week), "Dia a definir")
        
        # Formata o horário (objeto db.Time)
        horario = class_schedule.start_time.strftime('%H:%M') if class_schedule.start_time else "Horário a definir"
        
        return f"{dia_nome} às {horario}"

    def create_enrollment(self):
        if not self.form or not self.form.validate_on_submit():
            return ApiResponse.error(message="Dados inválidos.", data=self.form.errors)

        try:
            # 1. Verificar se a turma existe e tem vaga
            schedule = ClassSchedule.query.get(self.form.schedule_id.data)
            if not schedule:
                return ApiResponse.error(message="Turma não encontrada.")

            current_count = Enrollment.query.filter_by(schedule_id=schedule.id).count()
            if current_count >= schedule.max_capacity:
                return ApiResponse.error(message=f"Turma lotada! Limite de {schedule.max_capacity} alunos atingido.")

            # 2. Verificar se o aluno já está matriculado nesta mesma turma
            already_enrolled = Enrollment.query.filter_by(
                student_id=self.form.student_id.data,
                schedule_id=self.form.schedule_id.data
            ).first()
            if already_enrolled:
                return ApiResponse.error(message="Este aluno já está matriculado nesta turma.")

            # 3. Criar a matrícula
            new_enrollment = Enrollment(
                student_id=self.form.student_id.data,
                schedule_id=self.form.schedule_id.data
            )
            db.session.add(new_enrollment)
            db.session.commit()

            already_sent = WelcomeEmailLog.query.filter_by(student_id=self.form.student_id.data).first()
            student_id = self.form.student_id.data
        
            if not already_sent:
                student = Student.query.get(self.form.student_id.data)
                plan = Plan.query.get(self.form.plan_id.data)
                classroom = ClassSchedule.query.get(self.form.schedule_id.data)
                
                # Formata os horários da turma
                schedule_str = self.format_class_schedule(classroom) 
                
                # Chama a Task do Celery passando os dados necessários
                from app.tasks.email_tasks import send_welcome_email
                send_welcome_email.delay(
                    student_email=student.email,
                    student_name=student.full_name,
                    plan_name=plan.name,
                    duration=plan.duration_months,
                    class_name=classroom.name,
                    schedule=schedule_str,
                    enrollment_date=datetime.now().strftime('%d/%m/%Y'),
                    student_id=student_id,
                )
                
                # 3. Registra que o e-mail foi enviado


            return ApiResponse.success(message="Matrícula realizada com sucesso!")

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(message=f"Erro interno: {str(e)}")

    def list_enrollments(self):
        return Enrollment.query.all()