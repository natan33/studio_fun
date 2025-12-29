from flask import render_template, request, jsonify
from flask_login import login_required
from app.controllers.forms.academy_forms import ActivityForm
from app.services.AcademyService import AcademyService
from . import main # ou seu blueprint específico

@main.route('/academy/activities', methods=['GET', 'POST'])
@login_required
def page_activities():
    form = ActivityForm()
    service = AcademyService(form=form, request=request)

    if request.method == 'POST':
        response_data = service.create_activity()
        return jsonify(response_data.to_dict()), response_data.status_code
    
    activities = service.list_activities()
    return render_template('page-activities.html', form=form, activities=activities)