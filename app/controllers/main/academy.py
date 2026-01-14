from datetime import datetime
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import or_
from app.controllers.forms.academy_forms import ActivityForm, ClassScheduleForm, EnrollmentForm
from app.models.pages.academy import Activity, ClassSchedule
from app.services.AcademyService import AcademyService
from app.services.ActivitiesService import ActivitiesService
from . import main # ou seu blueprint específico


@main.route('/academy/activities', methods=['GET', 'POST'])
@login_required
def page_activities():
    form = ActivityForm()
    if request.method == 'POST':
        service = ActivitiesService(form=form, request=request)
        return service.main_form()
    activities = ActivitiesService.list_all(as_dict=False)
        
    return render_template('page-activities.html', form=form, activities=activities
    )


@main.route('/academy/schedules', methods=['GET', 'POST'])
@login_required
def page_schedules():
    form = ClassScheduleForm()
    service = AcademyService(form=form, request=request)
    
    # 1. FILTRAR DROP-DOWN: Pega apenas atividades 'Ativo'
    # Adicionamos .filter_by(status='Ativo') para não permitir cadastrar aula em atividade inativa
    activities = Activity.query.filter_by(status='Ativo').all()
    form.activity_id.choices = [(a.id, a.name) for a in activities]

    if request.method == 'POST':
        print("Form data received:", request.form.get('schedule_id'))
        if form.type_form.data == 'form_edit':
            return service.update_schedule()
        else:
            return service.create_schedule()
    
    # 2. FILTRAR LISTAGEM: Precisamos garantir que o service também filtre
    # Você tem duas opções: ajustar dentro do service ou filtrar aqui.
    schedules = service.list_schedules()
    
    # Se o seu service retorna uma lista de objetos, podemos filtrar via Python:
    active_schedules = [s for s in schedules if s.status == 'Ativo' and (s.is_active == True or s.is_active is None)]
    
    return render_template('page-schedules.html', 
                           form=form) # Enviamos apenas os ativos


@main.route('/academy/enrollments', methods=['GET', 'POST'])
@login_required
def page_enrollments():
    form = EnrollmentForm()
    service = AcademyService(form=form, request=request)
    
    # Carregamento dinâmico dos SelectFields
    
    form.student_id.choices = [] # Começa vazio para o AJAX preencher
    form.schedule_id.choices = []

    if request.method == 'POST':
        return service.create_enrollment()

    enrollments = service.list_enrollments()
    
    return render_template('page-enrollments.html', form=form, enrollments=enrollments)


@main.route('/academy/attendance')
@login_required
def page_attendance():
    # Carrega os horários para o dropdown de filtros
    schedules = ClassSchedule.query.join(Activity).filter(Activity.status == 'Ativo').all()
    today = datetime.now().strftime('%Y-%m-%d')
    from app.controllers.forms.academy_forms import MarkAttendanceForm
    form = MarkAttendanceForm()

    return render_template('attendance.html', schedules=schedules, today_date=today, form=form)