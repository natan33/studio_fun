from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

from sqlalchemy import extract, func
from app.models.pages.students import Student
from app.models.pages.finance import Expense, Invoice, Plan
from app import db
from app.utils.api_response import ApiResponse

class FinanceService:

    @staticmethod
    def get_finance_dashboard_stats():
        """Calcula os totais para os cards do financeiro"""
        hoje = datetime.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
        limite_inadimplencia = hoje - timedelta(days=90)

        # 1. Receita Prevista do Mês (Tudo que vence este mês)
        receita_mes = db.session.query(func.sum(Invoice.amount)).filter(
            Invoice.due_date >= primeiro_dia_mes,
            Invoice.status != 'cancelled'
        ).scalar() or 0

        # 2. Total Recebido (Tudo que já foi pago)
        total_pago = db.session.query(func.sum(Invoice.amount)).filter(
            Invoice.status == 'paid'
        ).scalar() or 0

        # 3. Total Atrasado (Pendente e Vencido, mas menor que 90 dias)
        total_atrasado = db.session.query(func.sum(Invoice.amount)).filter(
            Invoice.status == 'pending',
            Invoice.due_date < hoje,
            Invoice.due_date >= limite_inadimplencia
        ).scalar() or 0

        # 4. Contagem de Inadimplentes (Vencido há mais de 90 dias)
        count_inadimplentes = Invoice.query.filter(
            Invoice.status == 'pending',
            Invoice.due_date < limite_inadimplencia
        ).distinct(Invoice.student_id).count()

        return {
            'monthly_revenue': receita_mes,
            'total_paid': total_pago,
            'total_late': total_atrasado,
            'total_default': count_inadimplentes
        }


    @staticmethod
    def get_all_invoices(request=None):
        """Retorna faturas ativas (não canceladas) usando List Comprehension"""
        # Filtra para trazer apenas faturas que não foram inativadas
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        status = request.args.get('status')
        invoices = Invoice.query.join(Student).filter(Invoice.status != 'cancelled').all()
        # Aplica filtros adicionais se fornecidos
        if date_start and date_end:
            invoices = [inv for inv in invoices if date_start <= inv.due_date.strftime('%Y-%m-%d') <= date_end]
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        
        
        # List Comprehension para construir os dados do DataTables de forma performática
        data = [{
            "id": inv.id,
            "student_id": inv.student_id,
            "student_name": inv.student.full_name,
            "student_phone": inv.student.phone,
            "plan_name": inv.plan.name if inv.plan else "N/A",
            "due_date": inv.due_date.strftime('%d/%m/%Y'), # Formato brasileiro para o DataTables
            "amount": float(inv.amount),
            "status": inv.status,
            "financial_status": inv.financial_status
        } for inv in invoices]
        
        return data

    @staticmethod
    def generate_monthly_invoices():
        """
        Lógica para rodar todo dia 01: 
        Cria faturas para todos os alunos ativos baseada em seus planos.
        """
        # Esta função seria chamada por um CRON JOB ou manualmente
        pass

    
    @staticmethod
    def process_payment(invoice_id):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return False, "Fatura não encontrada"
        
        invoice.status = 'paid'
        invoice.payment_date = datetime.now()
        db.session.commit()
        return True, "Pagamento registrado com sucesso!"
    
        
    @staticmethod
    def delete_pix_file():
        """Localiza e deleta todos os arquivos PNG relacionados a um invoice_id específico"""
        root_dir = Path.cwd() / 'app'
        folder_path = os.path.join(root_dir, 'static', 'downloads', 'pix')
        
        if os.path.exists(folder_path):
            # Procuramos por qualquer arquivo que comece com 'pix_ID_'
            for filename in os.listdir(folder_path):
                    
                    try:
                        os.remove(os.path.join(folder_path, filename))
                        print(f"Arquivo {filename} deletado após baixa manual.")
                    except Exception as e:
                        print(f"Erro ao deletar arquivo após baixa: {e}")

    @staticmethod
    def cancel_payment(invoice_id=None):
        """Cancela uma fatura paga, revertendo seu status para pendente"""
        try:
            fatura = Invoice.query.get(invoice_id)
            if not fatura:
                return ApiResponse.error("Fatura não encontrada", 404)

            # 1. Atualiza o status no banco
            fatura.status = 'cancelled'
            fatura.updated_at = datetime.now(timezone.utc)
            
            # 2. Chama a função de limpeza que criamos (importada da sua task)
            FinanceService.delete_pix_file()
            
            db.session.commit()
            
            return ApiResponse.success(
                message="Pagamento inativado e QR Code removido com sucesso."
            )
            
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(f"Erro ao inativar: {str(e)}", 500)
        
    
    @staticmethod
    def get_financial_summary():
        try:
            # Definir o início e fim do mês atual para os cards de Receita
            today = datetime.now()
            first_day = today.replace(day=1, hour=0, minute=0, second=0)

            # 1. Receita total prevista (Mês Atual - Não cancelada)
            monthly_revenue = db.session.query(func.sum(Invoice.amount)).filter(
                Invoice.status != 'cancelled',
                Invoice.due_date >= first_day
            ).scalar() or 0

            # 2. Total que já caiu na conta (Total histórico ou mensal, conforme sua preferência)
            total_paid = db.session.query(func.sum(Invoice.amount)).filter(
                Invoice.status == 'paid'
            ).scalar() or 0

            # 3. Total de faturas pendentes que já venceram (Atrasadas)
            total_late = db.session.query(func.sum(Invoice.amount)).filter(
                Invoice.status == 'pending',
                Invoice.due_date < today # Vencimento menor que agora
            ).scalar() or 0

            # 4. Contagem de alunos inadimplentes únicos
            # Filtra faturas onde o status do financeiro é 'defaulter'
            total_default = db.session.query(func.count(func.distinct(Invoice.student_id))).filter(
                Invoice.financial_status == 'defaulter'
            ).scalar() or 0

            data = {
                "monthly_revenue": float(monthly_revenue),
                "total_paid": float(total_paid),
                "total_late": float(total_late),
                "total_default": int(total_default)
            }

            # Retorna usando seu padrão ApiResponse
            return data
        except Exception as e:
            return ApiResponse.error(str(e))
    
    @staticmethod
    def reverter_baixa(invoice_id=None):
        try:
            fatura = Invoice.query.get(invoice_id)
            if not fatura:
                return ApiResponse.error("Fatura não encontrada")
            
            if fatura.status == 'cancelled':
                return ApiResponse.error("Não é possível estornar uma fatura cancelada.")

            # Reverte o status para pendente
            fatura.status = 'pending'
            fatura.updated_at = db.func.now()
            
            db.session.commit()
            
            return ApiResponse.success(message="Baixa revertida! A fatura voltou para Pendente.")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(str(e))
        
    
    @staticmethod
    def get_dashboard_data():
        try:
            today = datetime.now()
            # 1. Total Recebido (Dinheiro que já entrou no caixa este mês)
            total_income = db.session.query(func.sum(Invoice.amount)).filter(
                Invoice.status == 'paid',
                extract('month', Invoice.payment_date) == today.month
            ).scalar() or 0

            # 2. Total Pago (Dinheiro que já saiu do caixa este mês)
            total_expense = db.session.query(func.sum(Expense.amount)).filter(
                Expense.status == 'paid',
                extract('month', Expense.payment_date) == today.month
            ).scalar() or 0

            data = {
                "income": float(total_income),
                "expense": float(total_expense),
                "profit": float(total_income - total_expense),
                "margin": round(((total_income - total_expense) / total_income * 100), 2) if total_income > 0 else 0
            }

            return ApiResponse.success(data=data)
        except Exception as e:
            return ApiResponse.error(str(e))
        
    @staticmethod
    def create_plan(name=None, price=None, duration_months=None): # Adicionado parâmetro
        try:
            # Verificação extra de negócio: evitar nomes duplicados
            if Plan.query.filter_by(name=name).first():
                return {"code": "ERROR", "message": "Já existe um plano com este nome."}

            # Criando o plano com a duração definida no modal
            new_plan = Plan(
                name=name, 
                price=price, 
                duration_months=duration_months # Salvando a duração
            )
            db.session.add(new_plan)
            db.session.commit()
            return {"code": "SUCCESS", "message": "Plano criado com sucesso!"}
        except Exception as e:
            db.session.rollback()
            return {"code": "ERROR", "message": f"Erro no banco: {str(e)}"}

    @staticmethod
    def update_plan_price(plan_id=None, new_price=None, duration_months=None): # Adicionado duration_months
        try:
            plan = Plan.query.get(plan_id)
            if not plan:
                return {"code": "ERROR", "message": "Plano não localizado."}
            
            plan.price = new_price
            plan.duration_months = duration_months # Atualizando a duração também
            
            db.session.commit()
            return {"code": "SUCCESS", "message": f"Plano '{plan.name}' atualizado!"}
        except Exception as e:
            db.session.rollback()
            return {"code": "ERROR", "message": f"Erro ao atualizar: {str(e)}"}
        
    @staticmethod
    def mark_as_paid(invoice_id=None, payment_data=None):
        try:
            from app import db
            from app.models import Invoice
            from datetime import datetime, timezone

            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return ApiResponse.error("Fatura não encontrada", 404)

            # Atualiza os campos com base no formulário
            invoice.status = 'paid'
            invoice.tp_pag = payment_data.get('tp_pag')
            invoice.description = payment_data.get('description')
            invoice.paid_at = datetime.now(timezone.utc)

            db.session.commit()
            return ApiResponse.success(f"Pagamento de registrado com sucesso!")

        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(f"Erro ao processar pagamento: {str(e)}", 500)