from app import  db
from celery_worker import celery
from app.models.pages.students import Student
from app.models.pages.finance import Invoice, Plan
from datetime import datetime
import calendar

@celery.task
def generate_monthly_invoices_task():
    """Gera faturas para todos os alunos ativos no mês atual"""
    hoje = datetime.now()
    # Define o vencimento para o dia 10 do mês atual (exemplo)
    due_date = hoje.replace(day=10).date()
    
    students = Student.query.filter_by(is_active=True).all()
    count = 0
    errors = 0
    
    for student in students:
        if not student.plan_id:
            errors += 1
            continue
        # Evita gerar faturas duplicadas para o mesmo mês/ano
        existing = Invoice.query.filter(
            Invoice.student_id == student.id,
            db.extract('month', Invoice.due_date) == hoje.month,
            db.extract('year', Invoice.due_date) == hoje.year
        ).first()
        
        if not existing and student.plan_id:
            plan = Plan.query.get(student.plan_id)
            new_invoice = Invoice(
                student_id=student.id,
                plan_id=plan.id,
                amount=plan.price,
                due_date=due_date,
                status='pending'
            )
            db.session.add(new_invoice)
            count += 1
            
    db.session.commit()
    if count == 0 and errors > 0:
        return f"0 faturas geradas. {errors} alunos foram ignorados por estarem sem plano vinculado."
    return f"Sucesso! {count} faturas geradas."