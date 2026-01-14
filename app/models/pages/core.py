from app import db
from datetime import datetime, timezone
from app.models.extensions import AuditMixin


class Setting(db.Model, AuditMixin):
    __tablename__ = 'settings'
    __table_args__ = {"schema": "core"}

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True) # Ex: "academy_name", "billing_day"
    value = db.Column(db.Text)

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

class AuditLog(db.Model, AuditMixin):
    __tablename__ = 'audit_logs'
    __table_args__ = {"schema": "core"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Quem fez?
    action = db.Column(db.String(100)) # O que fez? (INSERT, UPDATE)
    table_name = db.Column(db.String(50))
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)

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


class WelcomeEmailLog(db.Model, AuditMixin):
    __tablename__ = 'welcome_email_logs'
    __table_args__ = {"schema": "core"}
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'), nullable=False, unique=True)
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
