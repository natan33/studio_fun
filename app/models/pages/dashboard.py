# # Entrar no shell
# flask shell

# # Dentro do shell, execute:
# from app.models import Student, Invoice
# from datetime import datetime
# from app import db

# hoje = datetime.now()

# # 1. Verificar quantos alunos ativos existem
# ativos = Student.query.filter_by(is_active=True).all()
# print(f"Total de alunos ativos: {len(ativos)}")

# # 2. Verificar se esses alunos têm plano_id preenchido
# sem_plano = [s.name for s in ativos if not s.plan_id]
# print(f"Alunos ativos SEM plano: {sem_plano}")

# # 3. Listar as faturas deste mês para ver o status delas
# faturas_mes = Invoice.query.filter(db.extract('month', Invoice.due_date) == hoje.month,db.extract('year', Invoice.due_date) == hoje.year).all()

# print("\n--- Faturas encontradas no mês atual ---")
# for f in faturas_mes:
#     print(f"ID: {f.id} | Aluno ID: {f.student_id} | Status: '{f.status}' | Vencimento: {f.due_date}")