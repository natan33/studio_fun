from datetime import datetime
from . import api
from flask import request
from flask_login import login_required
from app.services.AttendanceService import AttendanceService
from app.utils.api_response import ApiResponse
from app.controllers.forms.academy_forms import MarkAttendanceForm



@api.route('/api/attendance/list-students')
@login_required
def api_list_students():
    s_id = request.args.get('schedule_id')
    date = request.args.get('date')
    data = AttendanceService.list_students_for_class(s_id, date)
    
    # Adicionamos a info de bloqueio em cada aluno da lista
    from app.models.pages.students import Student
    for student_data in data:
        print(f"DEBUG: Dados recebidos: {student_data}")
        student = Student.query.get(student_data['student_id'])
        student_data['is_blocked'] = student.is_blocked if student else False
        
    return ApiResponse.success(data=data)


@api.route('/api/attendance/evasion-risk')
@login_required
def api_evasion_risk():
    data = AttendanceService.get_evasion_risk()
    return ApiResponse.success(data=data)


@api.route('/api/attendance/monthly-report', methods=['GET'])
@login_required
def api_monthly_report():
    # O JS agora envia 'month_year' no formato "YYYY-MM"
    month_year = request.args.get('month_year')
    
    if month_year:
        try:
            # Divide a string "2026-01" em ano e mês
            year_str, month_str = month_year.split('-')
            year = int(year_str)
            month = int(month_str)
        except (ValueError, IndexError):
            # Caso venha um formato inválido, usa o atual
            month = datetime.now().month
            year = datetime.now().year
    else:
        # Padrão caso o parâmetro não exista
        month = datetime.now().month
        year = datetime.now().year
    
    # Chama o service com os valores tratados
    data = AttendanceService.get_monthly_report(month, year)
    
    if data is None:
        return ApiResponse.error(message="Erro ao gerar relatório mensal")
        
    return ApiResponse.success(data=data)



@api.route('/api/attendance/mark', methods=['POST'])
@login_required
def api_mark_attendance():
    form = MarkAttendanceForm()
    
    if form.validate_on_submit():
        # --- NOVA REGRA DE BLOQUEIO ---
        from app.models import Student # Importe o modelo Student
        student = Student.query.get(form.student_id.data)
        
        if student and student.is_blocked: # Usando a @property que criamos no Model
            return ApiResponse.error(
                message=f"BLOQUEIO FINANCEIRO: O aluno {student.full_name} está inadimplente há mais de 90 dias.",
                code="FINANCIAL_BLOCK"
            )
        # ------------------------------

        success, message = AttendanceService.mark_attendance(
            student_id=form.student_id.data,
            schedule_id=form.schedule_id.data,
            date_str=form.attendance_date.data.strftime('%Y-%m-%d'),
            status=form.status.data
        )
        
        if success:
            return ApiResponse.success(message=message)
        return ApiResponse.error(message=message)
    
    errors = ", ".join([f"{k}: {v[0]}" for k, v in form.errors.items()])
    return ApiResponse.error(message=f"Erro de validação: {errors}")


@api.route('/api/attendance/mark-all', methods=['POST'])
@login_required
def api_mark_all_presence():
    schedule_id = request.form.get('schedule_id')
    date_str = request.form.get('attendance_date')
    status = request.form.get('status', 'Presente')

    if not schedule_id or not date_str:
        return ApiResponse.error(message="Dados incompletos para marcar presença em massa.")

    # Chamamos o serviço para marcar todos
    success = AttendanceService.mark_all_enrolled(schedule_id, date_str, status)
    
    if success:
        return ApiResponse.success(message="Presença registrada para todos os alunos!")
    return ApiResponse.error(message="Erro ao registrar presenças.")

@api.route('/api/attendance/count-today', methods=['GET'])
@login_required
def api_attendance_count():
    # Pegamos a data e o schedule_id dos parâmetros da URL
    date_str = request.args.get('date')
    schedule_id = request.args.get('schedule_id', type=int)

    if not date_str or not schedule_id:
        return ApiResponse.error(message="Data e Turma são obrigatórias.")

    counts = AttendanceService.get_counts(schedule_id, date_str)
    return ApiResponse.success(data=counts)

@api.route('/api/attendance/available-months', methods=['GET'])
@login_required
def get_available_months():
    from datetime import datetime
    
    hoje = datetime.now()
    # Lista manual para evitar erros de 'locale' no servidor
    nomes_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    meses = []
    ano_atual = hoje.year
    
    # Gerar os meses do ano atual
    for i in range(12):
        mes_num = i + 1
        mes_nome = nomes_meses[i]
        
        meses.append({
            "value": f"{ano_atual}-{mes_num:02d}", # Formato: 2026-01
            "label": f"{mes_nome} / {ano_atual}",
            "current": mes_num == hoje.month
        })
        
    return ApiResponse.success(data=meses)