from flask import render_template, request, jsonify
from flask_login import login_required
from app.controllers.forms.academy_forms import ActivityForm, ClassScheduleForm, EnrollmentForm
from app.models.pages.academy import Activity
from app.services.AcademyService import AcademyService
from . import main # ou seu blueprint específico

@main.route('/academy/activities', methods=['GET', 'POST'])
@login_required
def page_activities():
    form = ActivityForm()
    service = AcademyService(form=form, request=request)

    if request.method == 'POST':
        return service.create_activity()
    
    activities = service.list_all(as_dict=False)
    return render_template('page-activities.html', form=form, activities=activities)


@main.route('/academy/schedules', methods=['GET', 'POST'])
@login_required
def page_schedules():
    form = ClassScheduleForm()
    service = AcademyService(form=form, request=request)
    
    # Preenche o dropdown de atividades dinamicamente
    activities = Activity.query.all()
    form.activity_id.choices = [(a.id, a.name) for a in activities]

    if request.method == 'POST':
        return service.create_schedule()
    
    schedules = service.list_schedules()
    return render_template('page-schedules.html', form=form, schedules=schedules)

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