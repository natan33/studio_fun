from flask import render_template, request, jsonify
from flask_login import login_required
from app.controllers.forms.academy_forms import ActivityForm, ClassScheduleForm, EnrollmentForm
from app.models.pages.academy import Activity
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
        return service.create_schedule()
    
    # 2. FILTRAR LISTAGEM: Precisamos garantir que o service também filtre
    # Você tem duas opções: ajustar dentro do service ou filtrar aqui.
    schedules = service.list_schedules()
    
    # Se o seu service retorna uma lista de objetos, podemos filtrar via Python:
    active_schedules = [s for s in schedules if s.status == 'Ativo']
    
    return render_template('page-schedules.html', 
                           form=form, 
                           schedules=active_schedules) # Enviamos apenas os ativos


@main.route('/academy/enrollments', methods=['GET', 'POST'])
@login_required
def page_enrollments():
    form = EnrollmentForm()
    service = AcademyService(form=form, request=request)
    
    # Carregamento dinâmico dos SelectFields
    from app.models.pages.academy import ClassSchedule
    from app.models.pages.students import Student
    form.student_id.choices = [(s.id, s.full_name) for s in Student.query.order_by('full_name').all()]
    
    schedules = ClassSchedule.query.all()
    form.schedule_id.choices = [
        (sch.id, f"{sch.activity_ref.name} - {sch.day_of_week} às {sch.start_time.strftime('%H:%M')}") 
        for sch in schedules
    ]

    if request.method == 'POST':
        return service.create_enrollment()

    enrollments = service.list_enrollments()
    
    return render_template('page-enrollments.html', form=form, enrollments=enrollments)