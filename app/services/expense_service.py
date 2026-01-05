from app.models import Expense
from app import db
from app.utils.api_response import ApiResponse
from datetime import datetime

class ExpenseService:
    @staticmethod
    def get_all_expenses():
        try:
            expenses = Expense.query.order_by(Expense.due_date.asc()).all()
            return ApiResponse.success(
                data=[e.to_dict() for e in expenses],
                message="Despesas listadas com sucesso"
            )
        except Exception as e:
            return ApiResponse.error(str(e))

    @staticmethod
    def create_expense(data):
        try:
            nova_despesa = Expense(
                description=data.get('description'),
                category=data.get('category'),
                amount=data.get('amount'),
                due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date(),
                status='pending'
            )
            db.session.add(nova_despesa)
            db.session.commit()
            return ApiResponse.success(message="Despesa cadastrada!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    @staticmethod
    def pagar_despesa(expense_id):
        try:
            expense = Expense.query.get(expense_id)
            if not expense:
                return ApiResponse.error("Despesa não encontrada")
            
            expense.status = 'paid'
            expense.payment_date = datetime.now().date()
            db.session.commit()
            return ApiResponse.success(message="Conta marcada como paga!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    @staticmethod
    def get_expense_by_id(expense_id=None):
        try:
            expense = Expense.query.get(expense_id)
            if not expense:
                return ApiResponse.error("Despesa não encontrada")
            
            data = expense.to_dict()
            # Adicionamos a data formatada para o input type="date" do HTML (YYYY-MM-DD)
            data['due_date_iso'] = expense.due_date.strftime('%Y-%m-%d')
            return ApiResponse.success(data=data)
        except Exception as e:
            return ApiResponse.error(str(e))

    @staticmethod
    def undo_payment(expense_id=None):
        try:
            expense = Expense.query.get(expense_id)
            if not expense:
                return ApiResponse.error("Despesa não encontrada")
            
            expense.status = 'pending'
            expense.payment_date = None
            db.session.commit()
            return ApiResponse.success(message="Pagamento estornado! A conta está pendente novamente.")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    @staticmethod
    def delete_expense(expense_id=None):
        try:
            expense = Expense.query.get(expense_id)
            if not expense:
                return ApiResponse.error("Despesa não encontrada")
            
            db.session.delete(expense)
            db.session.commit()
            return ApiResponse.success(message="Despesa removida com sucesso.")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))

    @staticmethod
    def update_expense(expense_id=None, data=None):
        try:
            expense = Expense.query.get(expense_id)
            if not expense:
                return ApiResponse.error("Despesa não encontrada")

            expense.description = data.get('description')
            expense.category = data.get('category')
            expense.amount = data.get('amount')
            expense.due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
            
            db.session.commit()
            return ApiResponse.success(message="Despesa atualizada com sucesso!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))