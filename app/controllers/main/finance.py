from app.controllers.forms.forms_finance import PlanForm
from app.models.pages.finance import Plan
from . import main 
from flask import render_template, request
from flask_login import login_required
from app.services.FinanceService import FinanceService

@main.route('/finance/contas-receber', methods=['GET'])
@login_required
def finance_contas_receber():
    service = FinanceService()
    data = service.get_finance_dashboard_stats()
    return render_template('finance/finance_contas_receber.html', data=data)

@main.route('/finance/expense', methods=['GET'])
@login_required
def finance_expense():
    from app.controllers.forms.forms_finance import ExpenseForm
    form = ExpenseForm()
    return render_template('finance/finance_expense.html', form=form)

@main.route("/finance/dashboard", methods=['GET'])
@login_required
def finance_dashboard():
    form = PlanForm()
    planos = Plan.query.all()
    
    # IDs e Nomes dos planos para o primeiro select
    form.plan_id.choices = [(plan.id, plan.name) for plan in planos]
    
    # VALORES FIXOS para a duração (conforme definido no PlanForm original)
    # O primeiro valor da tupla deve ser o número de meses
    
    service = FinanceService()
    data = service.get_finance_dashboard_stats()
    return render_template('finance/financeiro_dashboard.html', data=data, form=form, planos_lista=planos)