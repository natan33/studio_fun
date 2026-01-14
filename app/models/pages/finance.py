
from app import db
from datetime import datetime, timezone
from app.models.extensions import AuditMixin

class Plan(db.Model, AuditMixin):
    __tablename__ = 'plans'
    __table_args__ = {"schema": "finance"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50)) # Mensal, Trimestral
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer)

    # Novo campo: 1 para mensal, 3 para trimestral, 12 para anual, etc.
    duration_months = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # SENIOR TIP: onupdate garante que o Postgres/SQLAlchemy atualize a data 
    # automaticamente em cada modificação do registro.
    update_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def auto_repair_durations(cls):
        """Ajusta automaticamente a duração baseada no nome do plano (Bug Fix)"""
        plans = cls.query.all()
        updates = 0
        
        for plan in plans:
            name_lower = plan.name.lower()
            old_val = plan.duration_months
            
            # 1. Primeiro checamos os específicos e longos
            if 'trimestre' in name_lower or 'tri' in name_lower:
                plan.duration_months = 3
            elif 'semestre' in name_lower or 'sem' in name_lower:
                plan.duration_months = 6
            # 2. Para o Anual, evitamos nomes que tenham 'mensal'
            elif ('anual' in name_lower or 'ano' in name_lower) and 'mensal' not in name_lower:
                plan.duration_months = 12
            # 3. Se for mensal ou qualquer outro, cai no 1
            else:
                plan.duration_months = 1
            
            if old_val != plan.duration_months:
                updates += 1
                print(f"Corrigindo '{plan.name}': {old_val} -> {plan.duration_months}")
        
        try:
            db.session.commit()
            return f"Sucesso! {updates} planos corrigidos."
        except Exception as e:
            db.session.rollback()
            return f"Erro: {str(e)}"

class Invoice(db.Model, AuditMixin):
    __tablename__ = 'invoices'
    __table_args__ = {"schema": "finance"}

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('finance.plans.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False) # Data de Vencimento
    payment_date = db.Column(db.DateTime) # Data que o aluno pagou
    
    # Status: 'pending' (pendente), 'paid' (pago), 'cancelled' (cancelado)
    status = db.Column(db.String(20), default='pending')
    
    # Campos para Integração de Cobrança
    payment_method = db.Column(db.String(20)) # 'pix' ou 'boleto'
    external_id = db.Column(db.String(100)) # ID da transação no Gateway (Mercado Pago, Asaas, etc)
    pix_copy_paste = db.Column(db.Text) # Código Pix Copia e Cola

    paid_at = db.Column(db.DateTime, nullable=True)
    description_paid = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    update_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


    # Relacionamentos
    student = db.relationship('Student', backref='invoices')
    plan = db.relationship('Plan')

    @property
    def financial_status(self):
        """Retorna o status calculado para o Front-end"""
        if self.status == 'paid':
            return 'em_dia'
        
        hoje = datetime.now().date()
        if hoje > self.due_date:
            atraso = (hoje - self.due_date).days
            if atraso > 90:
                return 'inadimplente' # Bloqueio automático
            return 'atrasado'
            
        return 'pendente'
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Expense(db.Model, AuditMixin):
    __tablename__ = 'expenses'
    __table_args__ = {"schema": "finance"}
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False) # Ex: Aluguel, Luz, Professor X
    category = db.Column(db.String(50), nullable=False)    # Ex: Fixo, Variável, Pessoal
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date, nullable=True)       # Data em que foi pago de fato
    status = db.Column(db.String(20), default='pending')   # 'pending' ou 'paid'
    observation = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "category": self.category,
            "amount": float(self.amount),
            "due_date": self.due_date.strftime('%d/%m/%Y'),
            "payment_date": self.payment_date.strftime('%d/%m/%Y') if self.payment_date else None,
            "status": self.status
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()