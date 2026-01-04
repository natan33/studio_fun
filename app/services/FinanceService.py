from datetime import datetime, timedelta

from sqlalchemy import func
from app.models.pages.students import Student
from app.models.pages.finance import Invoice
from app import db

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
    def get_all_invoices():
        """Retorna todas as faturas para o DataTables"""
        invoices = Invoice.query.join(Student).all()
        
        data = []
        for inv in invoices:
            # A lógica de 'financial_status' que criamos no Model faz o trabalho duro
            data.append({
                "id": inv.id,
                "student_id": inv.student_id,
                "student_name": inv.student.full_name,
                "plan_name": inv.plan.name if inv.plan else "N/A",
                "due_date": inv.due_date.strftime('%Y-%m-%d'),
                "amount": float(inv.amount),
                "status": inv.status,
                "financial_status": inv.financial_status # 'em_dia', 'atrasado' ou 'inadimplente'
            })
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