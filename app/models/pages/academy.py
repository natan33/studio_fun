from datetime import datetime, timezone
from app import db


class Modality(db.Model):
    __tablename__ = 'modalities'
    __table_args__ = {"schema": "academy"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # Ex: Pilates, Zumba
    description = db.Column(db.Text)

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


class Activity(db.Model):
    __tablename__ = 'activities'
    __table_args__ = {"schema": "academy"}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relacionamento para facilitar a busca de turmas de uma atividade
    schedules = db.relationship('ClassSchedule', backref='activity', lazy=True)


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

# Atualize o seu ClassSchedule para garantir a relação
class ClassSchedule(db.Model):
    __tablename__ = 'class_schedules'
    __table_args__ = {"schema": "academy"}
    
    id = db.Column(db.Integer, primary_key=True)
    # FK para a nova tabela
    activity_id = db.Column(db.Integer, db.ForeignKey('academy.activities.id'), nullable=False)
    
    day_of_week = db.Column(db.String(20)) # Ex: 'Segunda-feira'
    start_time = db.Column(db.Time, nullable=False)
    max_capacity = db.Column(db.Integer, default=15)
    
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


class Attendance(db.Model):
    __tablename__ = 'attendance'
    __table_args__ = {"schema": "academy"}

    id = db.Column(db.Integer, primary_key=True)
    # No arquivo academy.py
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id', ondelete='CASCADE'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('academy.class_schedule.id'))
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())

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


class AttendanceSummary(db.Model):
    """Tabela de performance para relatórios rápidos sem precisar contar milhões de linhas"""
    __tablename__ = 'attendance_summary'
    __table_args__ = {"schema": "academy"}

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'))
    total_lessons = db.Column(db.Integer, default=0)
    last_presence = db.Column(db.Date)

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


class ClassStudent(db.Model):
    __tablename__ = 'class_students'
    __table_args__ = {"schema": "academy"}

    student_id = db.Column(db.Integer, db.ForeignKey('students.students.id'), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('academy.class_schedule.id'), primary_key=True)
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


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