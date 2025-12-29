from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class StudentForm(FlaskForm):
    # ... outros campos (full_name, cpf, birth_date) ...
    full_name = StringField('Nome Completo', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[Optional()])
    birth_date = DateField('Data de Nascimento', validators=[Optional()])

    # Adicione este campo aqui:
    weight = FloatField('Peso (kg)', validators=[Optional()])
    
    blood_type = SelectField('Tipo Sanguíneo', choices=[
        ('', 'Selecione'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), 
        ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    
    medical_notes = TextAreaField('Observações Médicas', validators=[Optional()])
    submit = SubmitField('Salvar')