from flask import render_template
from flask_login import login_required

from app.services.DashboardService import DashboardService
from . import main

@main.route('/', methods=['GET', 'POST'])
@main.route('/portal', methods=['GET', 'POST'])
@login_required
def index():
    service = DashboardService()
    data = service.get_full_dashboard()
    return render_template('index.html', data=data)


       
