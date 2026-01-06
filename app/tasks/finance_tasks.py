import os
from pathlib import Path
import time
from app import  db
from app.tasks.financial_tasks import generate_and_send_invoice_pix
from celery_worker import celery
from app.models.pages.students import Student
from app.models.pages.finance import Invoice, Plan
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

@celery.task(name='app.tasks.finance_tasks.generate_monthly_invoices_task')
def generate_monthly_invoices_task():
    """Gera faturas para alunos ativos respeitando a duração de cada plano"""
    hoje_dt = datetime.now()
    hoje_date = hoje_dt.date()
    
    # Define o vencimento padrão para o dia 10
    due_date = hoje_dt.replace(day=10).date()
    month_ref = hoje_dt.strftime('%B/%Y')
    
    students = Student.query.filter_by(is_active=True).all()
    count = 0
    errors = 0
    
    for student in students:
        if not student.plan_id:
            errors += 1
            continue

        plan = Plan.query.get(student.plan_id)
        if not plan:
            continue

        existing = None

        # --- LÓGICA PARA PLANO MENSAL (1 mês) ---
        if plan.duration_months == 1:
            existing = Invoice.query.filter(
                Invoice.student_id == student.id,
                Invoice.status != 'cancelled',
                db.extract('month', Invoice.due_date) == hoje_dt.month,
                db.extract('year', Invoice.due_date) == hoje_dt.year
            ).first()

        # --- LÓGICA PARA PLANOS LONGOS (Trimestral, Anual, etc) ---
        else:
            last_invoice = Invoice.query.filter(
                Invoice.student_id == student.id,
                Invoice.status != 'cancelled'
            ).order_by(Invoice.due_date.desc()).first()

            if last_invoice:
                # Calcula quando acaba a cobertura da última fatura
                next_billing_date = last_invoice.due_date + relativedelta(months=plan.duration_months)
                
                # Se ainda não chegou o dia de cobrar de novo, define como 'existing' para pular
                if hoje_date < next_billing_date:
                    existing = last_invoice
                    print(f"   [COBERTURA ATIVA] Aluno {student.full_name} em plano {plan.name} até {next_billing_date}")

        # Se 'existing' estiver preenchido, pula a geração
        if existing:
            print(f"   [IGNORADO] Aluno {student.full_name} já possui fatura ativa ou está em período de cobertura.")
            continue
        
        # --- GERAÇÃO DA FATURA ---
        try:
            new_invoice = Invoice(
                student_id=student.id,
                plan_id=plan.id,
                amount=plan.price,
                due_date=due_date,
                status='pending'
            )
            db.session.add(new_invoice)
            db.session.commit() # Commit aqui para gerar o ID
            
            # Envia para a fila de disparo de PIX e E-mail
            generate_and_send_invoice_pix.delay(
                invoice_id=new_invoice.id,
                amount=float(plan.price),
                student_name=student.full_name,
                student_email=student.email,
                month_ref=month_ref
            )
            count += 1
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar fatura do aluno {student.id}: {e}")
            errors += 1

    return f"Sucesso! {count} faturas geradas. {errors} problemas encontrados."


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