from app.controllers.forms.forms_finance import ExpenseForm
from . import api
from flask_login import login_required
from app.utils.api_response import ApiResponse
from app.services.expense_service import ExpenseService
from flask import request

@api.route('/api/finance/expenses', methods=['GET'])
@login_required
def list_expenses():
    return ExpenseService.get_all_expenses()

@api.route('/api/finance/expenses/add', methods=['POST'])
@login_required
def add_expense():
    data = request.json
    return ExpenseService.create_expense(data)

@api.route('/api/finance/expenses/save', methods=['POST'])
@login_required
def save_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        data = request.form.to_dict() # Pega os dados do formulário
        
        # Lógica de decisão
        if data.get('form_type') == 'update':
            expense_id = data.get('expense_id')
            return ExpenseService.update_expense(expense_id, data)
        else:
            return ExpenseService.create_expense(data)
            
    return ApiResponse.error("Erro na validação do formulário")

@api.route('/api/finance/expenses/<int:id>/pay', methods=['POST'])
@login_required
def pay_expense(id):
    return ExpenseService.pagar_despesa(id)

# Definindo as novas rotas no seu Blueprint de finanças
@api.route('/api/finance/expenses/<int:id>', methods=['GET'])
@login_required
def get_expense(id):
    """Retorna os dados de uma despesa específica para edição"""
    return ExpenseService.get_expense_by_id(id)

@api.route('/api/finance/expenses/<int:id>/undo', methods=['POST'])
@login_required
def undo_expense_payment(id):
    """Estorna o pagamento de uma despesa"""
    return ExpenseService.undo_payment(id)

@api.route('/api/finance/expenses/<int:id>/delete', methods=['DELETE'])
@login_required
def delete_expense(id):
    """Exclui permanentemente uma despesa"""
    return ExpenseService.delete_expense(id)

@api.route('/api/finance/expenses/<int:id>/update', methods=['POST'])
@login_required
def update_expense(id):
    """Atualiza os dados de uma despesa existente"""
    data = request.json
    return ExpenseService.update_expense(id, data)