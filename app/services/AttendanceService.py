from app.models.pages.academy import Attendance, ClassSchedule, Activity
from app.models.pages.academy import Enrollment # Assumindo que você tem matrículas
from app import db
from sqlalchemy import extract, func, text
from datetime import datetime, timedelta
from calendar import monthrange
from datetime import datetime

from app.models.pages.students import Student
from app.utils.api_response import ApiResponse

class AttendanceService:
    @staticmethod
    def list_students_for_class(schedule_id, date_str):
        # 1. Busca alunos matriculados na atividade deste horário
        schedule = ClassSchedule.query.get(schedule_id)
        print(schedule)
        if not schedule:
            return []

        # Pega alunos ativos na atividade vinculada a esse schedule
        enrollments = Enrollment.query.filter_by(
                schedule_id=schedule.id, # <--- MUDE PARA O NOME CORRETO DO CAMPO NO MODELO ENROLLMENT
                status='Ativo'
            ).all()

        data = []
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        for enr in enrollments:
            # Busca se já existe registro de presença para este aluno neste dia/aula
            att = Attendance.query.filter_by(
                student_id=enr.student_id,
                schedule_id=schedule_id,
                date=date_obj
            ).first()

            data.append({
                'student_id': enr.student_id,
                'student_name': enr.student.full_name,
                'plan_name':"Ativo",
                'status_matricula': enr.status,
                'current_status': att.status if att else None,
                'last_attendance': "---" # Lógica extra opcional
            })
        return data

    @staticmethod
    def mark_attendance(student_id=None, schedule_id=None, date_str=None, status=None):
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Tenta encontrar registro existente (Check-in ou Manual)
            att = Attendance.query.filter_by(
                student_id=student_id,
                schedule_id=schedule_id,
                date=date_obj
            ).first()

            if att:
                att.status = status
            else:
                att = Attendance(
                    student_id=student_id,
                    schedule_id=schedule_id,
                    date=date_obj,
                    status=status
                )
                db.session.add(att)
            
            db.session.commit()
            return True, f"Presença de {status} registrada."
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def mark_all_enrolled(schedule_id=None, date_str=None, status=None):
        try:
            # Busca todos os alunos ativos matriculados nesta turma (schedule)
            enrollments = Enrollment.query.filter_by(schedule_id=schedule_id, status='Ativo').all()
            
            for enrollment in enrollments:
                # Verifica se já existe um registro para este aluno nesta data/turma
                attendance = Attendance.query.filter_by(
                    student_id=enrollment.student_id,
                    schedule_id=schedule_id,
                    date=date_str
                ).first()

                if not attendance:
                    # Se não existe, cria um novo
                    attendance = Attendance(
                        student_id=enrollment.student_id,
                        schedule_id=schedule_id,
                        date=date_str,
                        status=status
                    )
                    db.session.add(attendance)
                else:
                    # Se já existe (ex: aluno tinha falta e mudou para presença em massa), atualiza
                    attendance.status = status
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao marcar todos: {e}")
            return False

    @staticmethod
    def get_evasion_risk():
        try:
            # 1. Definir o mês atual
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # 2. Buscar todos os alunos ativos
            students = Student.query.filter_by(status='Ativo').all()
            
            # 3. Definir um número base de aulas no mês para o cálculo (ex: 8 aulas)
            # Você pode ajustar isso ou buscar de uma tabela de configurações
            total_aulas_previstas = 8 
            
            risk_list = []
            
            for student in students:
                # 4. Contar presenças do aluno no mês atual
                presencas = db.session.query(Attendance).filter(
                    Attendance.student_id == student.id,
                    Attendance.status == 'Presente',
                    extract('month', Attendance.date) == current_month,
                    extract('year', Attendance.date) == current_year
                ).count()
                
                # 5. Calcular a frequência
                # Evita divisão por zero se total_aulas_previstas for 0
                percentual = (presencas / total_aulas_previstas) * 100 if total_aulas_previstas > 0 else 0
                
                # 6. Se a frequência for menor que 50%, adiciona ao alerta
                if percentual < 50:
                    risk_list.append({
                        "name": student.full_name,
                        "rate": round(percentual, 1) # Ex: 37.5
                    })
            
            return risk_list

        except Exception as e:
            print(f"Erro ao calcular risco de evasão: {str(e)}")
            return []

    @staticmethod
    def get_monthly_report(month=None, year=None):
            try:
                # 1. Descobre quantos dias tem o mês (ex: 31)
                num_days = monthrange(year, month)[1]
                
                # 2. Busca todos os alunos ativos (ajuste 'status' conforme seu modelo)
                students = Student.query.filter_by(is_active=True).order_by(Student.full_name).all()
                
                report_data = []
                
                for student in students:
                    # 3. Busca presenças do aluno no mês/ano específico
                    attendances = Attendance.query.filter(
                        Attendance.student_id == student.id,
                        extract('month', Attendance.date) == month,
                        extract('year', Attendance.date) == year
                    ).all()
                    
                    # 4. Mapeia os dias: {dia: status_inicial}
                    # Pega a primeira letra: 'Presente' -> 'P', 'Falta' -> 'F'
                    att_map = {att.date.day: att.status[0].upper() for att in attendances}
                    
                    days_list = []
                    for day in range(1, num_days + 1):
                        # Se não houver registro no dia, preenche com "-"
                        days_list.append(att_map.get(day, "-"))
                    
                    # 5. Adiciona ao relatório
                    report_data.append({
                        'name': student.full_name,
                        'days': days_list,
                        'total_p': list(att_map.values()).count('P')
                    })
                    
                return {
                    'days_in_month': num_days,
                    'report': report_data
                }
            except Exception as e:
                print(f"Erro ao gerar relatório mensal no Service: {str(e)}")
                return None
    
    @staticmethod
    def get_counts(schedule_id, date_str):
        try:
            # 1. Total de alunos matriculados nesta turma
            total_enrolled = Enrollment.query.filter_by(
                schedule_id=schedule_id, 
                status='Ativo'
            ).count()

            # 2. Contagem por status na tabela de presença
            presentes = Attendance.query.filter_by(
                schedule_id=schedule_id, 
                date=date_str, 
                status='Presente'
            ).count()

            faltas = Attendance.query.filter_by(
                schedule_id=schedule_id, 
                date=date_str, 
                status='Falta'
            ).count()

            # 3. Pendentes são os matriculados que ainda não tem registro hoje
            pendentes = total_enrolled - (presentes + faltas)

            return {
                'presentes': presentes,
                'faltas': faltas,
                'pendentes': max(0, pendentes), # Garante que não seja negativo
                'total': total_enrolled
            }
        except Exception as e:
            print(f"Erro ao contar presenças: {e}")
            return {'presentes': 0, 'faltas': 0, 'pendentes': 0, 'total': 0}
        
    @staticmethod
    def list_schedule_options(request=None):
        from app.models.pages.academy import ClassSchedule, Activity

        # 1. Pegamos o termo de busca (se houver)
        search = request.args.get('q', '')

        # 2. Montamos a BASE da query (Apenas a receita, sem .all() ainda)
        # Filtramos apenas Atividades com status 'Ativo'
        query = ClassSchedule.query.join(Activity).filter(Activity.status == 'Ativo')

        # 3. Adicionamos o filtro de busca DINAMICAMENTE
        if search:
            query = query.filter(
                or_(
                    Activity.name.ilike(f'%{search}%'),
                    ClassSchedule.day_of_week.ilike(f'%{search}%')
                )
            )

        # 4. AGORA SIM executamos a query no banco de dados
        schedules = query.all()
        
        # 5. Formatamos o resultado para o Select do Frontend
        options = [
            {
                "id": s.id,
                "display_text": f"{s.activity_ref.name} - {s.day_of_week} às {s.start_time.strftime('%H:%M')}"
            } 
            for s in schedules
        ]
        
        return ApiResponse.success(data=options)