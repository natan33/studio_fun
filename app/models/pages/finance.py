
from app import db
from datetime import datetime, timezone

class Plan(db.Model):
    __tablename__ = 'plans'
    __table_args__ = {"schema": "finance"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50)) # Mensal, Trimestral
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer)

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

class Invoice(db.Model):
    __tablename__ = 'invoices'
    __table_args__ = {"schema": "finance"}

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'))
    value = db.Column(db.Numeric(10, 2))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='open') # open, paid, overdue


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