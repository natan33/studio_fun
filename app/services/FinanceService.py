from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

from sqlalchemy import func
from app.models.pages.students import Student
from app.models.pages.finance import Invoice
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
    def mark_as_paid(invoice_id):
        """Dá baixa manual em uma fatura"""
        invoice = Invoice.query.get(invoice_id)
        if invoice:
            invoice.status = 'paid'
            invoice.payment_date = datetime.now()
            db.session.commit()
            return True, "Pagamento registrado!"
        return False, "Fatura não encontrada."
    
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
    def mark_as_paid(invoice_id=None):
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return False, "Fatura não encontrada."
        
        if invoice.status == 'paid':
            return False, "Esta fatura já foi paga."

        try:
            invoice.status = 'paid'
            invoice.payment_date = datetime.now()
            db.session.commit()
            return True, "Pagamento registado com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao processar: {str(e)}"
        
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
        """Calcula os totais para os cards do dashboard usando list compression"""
        # Pega todas as faturas que não foram canceladas
        invoices = Invoice.query.filter(Invoice.status != 'cancelled').all()

        # Cálculos usando compressão de lista
        # 1. Receita total prevista (tudo que não foi cancelado)
        monthly_revenue = sum([float(i.amount) for i in invoices])
        
        # 2. Total que já caiu na conta
        total_paid = sum([float(i.amount) for i in invoices if i.status == 'paid'])
        
        # 3. Total de faturas pendentes que já venceram
        total_late = sum([float(i.amount) for i in invoices if i.status == 'pending' and i.financial_status == 'late'])

        # 4. Contagem de alunos inadimplentes (ex: financial_status == 'inadimplente')
        # Aqui contamos IDs de alunos únicos que estão nesse estado
        total_default = len(list(set([i.student_id for i in invoices if i.financial_status == 'defaulter'])))

        data = {
            "monthly_revenue": monthly_revenue,
            "total_paid": total_paid,
            "total_late": total_late,
            "total_default": total_default
        }

        return data
    
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