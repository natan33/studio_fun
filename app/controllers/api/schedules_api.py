from . import api
from flask_login import login_required


@api.route('/api/schedules', methods=['GET'])
@login_required
def get_schedules():
    from app.services.SchedulesService import SchedulesService
    
    service = SchedulesService()
    return service.list_schedules()


@api.route('/api/schedules/<int:id>/students', methods=['GET'])
@login_required
def get_schedule_students(id):
    from app.services.SchedulesService import SchedulesService
    
    service = SchedulesService()
    return service.list_schedule_students(id=id)

@api.route('/api/schedules/<int:id>', methods=['GET'])
@login_required
def get_schedule_detail(id):
    from app.services.SchedulesService import SchedulesService
    
    service = SchedulesService()
    return service.get_schedule_detail(id=id)

@api.route('/api/schedules/<int:id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    from app.services.SchedulesService import SchedulesService
    
    service = SchedulesService()
    return service.delete_schedule(id=id)

@api.route('/page-schedules', methods=['POST']) # ou sua rota de salvamento
@login_required
def save_schedule():
    from app.services.SchedulesService import SchedulesService
    from app.controllers.forms.academy_forms import ClassScheduleForm
    from flask import request

    form = ClassScheduleForm(request.form)
    service = SchedulesService(form=form, request=request)
    return service.save_schedule()