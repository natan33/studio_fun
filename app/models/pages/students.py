from app import db
from datetime import datetime, timezone

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {"schema": "students"}

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, index=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    
    # Controle de Status (Resolve seu erro)
    is_active = db.Column(db.Boolean, default=True)

    # Informações de Saúde (Detalhamento)
    blood_type = db.Column(db.String(5))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    medical_notes = db.Column(db.Text) # Alergias, cirurgias, etc.
    
    # Contato de Emergência
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))

    # Endereço
    postal_code = db.Column(db.String(10)) # CEP
    address = db.Column(db.String(150))
    address_number = db.Column(db.String(10))
    city = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # SENIOR TIP: onupdate garante que o Postgres/SQLAlchemy atualize a data 
    # automaticamente em cada modificação do registro.
    update_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


    # Relacionamento com dados de saúde
    health_data = db.relationship('StudentHealth', backref='student', uselist=False)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'cpf': self.cpf,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StudentHealth(db.Model):
    __tablename__ = 'student_health_data'
    __table_args__ = {"schema": "students"}

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'))
    blood_type = db.Column(db.String(3))
    medical_notes = db.Column(db.Text)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)


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
    def get_student_id(cls,student_id=None):
        return cls.query.filter_by(student_id=student_id).first()