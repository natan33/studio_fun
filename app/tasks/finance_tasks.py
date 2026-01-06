import os
from pathlib import Path
import time
from app import  db
from app.tasks.financial_tasks import generate_and_send_invoice_pix
from celery_worker import celery
from app.models.pages.students import Student
from app.models.pages.finance import Invoice, Plan
from datetime import datetime
import calendar

@celery.task(name='app.tasks.finance_tasks.generate_monthly_invoices_task')
def generate_monthly_invoices_task():
    """Gera faturas para todos os alunos ativos no mês atual, ignorando as canceladas"""
    hoje = datetime.now()
    # Define o vencimento para o dia 10 do mês atual
    due_date = hoje.replace(day=10).date()
    # Nome do mês para o e-mail (ex: Janeiro/2026)
    month_ref = hoje.strftime('%B/%Y')
    
    students = Student.query.filter_by(is_active=True).all()
    count = 0
    errors = 0
    
    for student in students:
        if not student.plan_id:
            errors += 1
            continue

        # Buscamos faturas que NÃO estejam canceladas
        existing = Invoice.query.filter(
            Invoice.student_id == student.id,
            Invoice.status != 'cancelled',
            db.extract('month', Invoice.due_date) == hoje.month,
            db.extract('year', Invoice.due_date) == hoje.year
        ).first()
        
        if not existing:
            plan = Plan.query.get(student.plan_id)
            if plan:
                # 1. Criamos o objeto da fatura
                new_invoice = Invoice(
                    student_id=student.id,
                    plan_id=plan.id,
                    amount=plan.price,
                    due_date=due_date,
                    status='pending'
                )
                db.session.add(new_invoice)
                
                # 2. IMPORTANTE: Commitamos agora para gerar o ID da fatura
                try:
                    db.session.commit()
                    
                    # 3. Agora enviamos para a fila do Celery com os dados REAIS
                    generate_and_send_invoice_pix.delay(
                        invoice_id=new_invoice.id, # ID real do banco
                        amount=float(plan.price),  # Preço real do plano
                        student_name=student.full_name, # Use 'name' ou 'username' conforme seu Model
                        student_email=student.email,
                        month_ref=month_ref
                    )
                    count += 1
                except Exception as e:
                    db.session.rollback()
                    print(f"Erro ao salvar fatura do aluno {student.id}: {e}")
                    errors += 1

    return f"Sucesso! {count} faturas geradas e enviadas para fila de e-mail. {errors} problemas encontrados."



@celery.task(name='app.tasks.finance_tasks.cleanup_old_pix_files')
def cleanup_old_pix_files():
    """Remove arquivos de QR Code com mais de 24 horas de criação"""
    root_dir = Path.cwd() / 'app'
    folder_path = os.path.join(root_dir, 'static', 'downloads', 'pix')
    
    if not os.path.exists(folder_path):
        return "Pasta não encontrada."

    now = time.time()
    cutoff = now - (24 * 60 * 60) # 24 horas em segundos
    count = 0

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Verifica se é um arquivo e se a data de modificação é anterior ao cutoff
        if os.path.isfile(file_path):
            if os.path.getmtime(file_path) < cutoff:
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"Erro ao deletar {filename}: {e}")

    return f"Limpeza concluída. {count} arquivos removidos."