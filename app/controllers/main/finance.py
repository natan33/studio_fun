from . import main 
from flask import render_template, request
from flask_login import login_required
from app.services.FinanceService import FinanceService

@main.route('/finance', methods=['GET'])
@login_required
def finance_dashboard():
    service = FinanceService()
    data = service.get_finance_dashboard_stats()
    return render_template('finance_dashboard.html', data=data)