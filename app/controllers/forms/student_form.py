from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class StudentForm(FlaskForm):
    # Dados Pessoais
    full_name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=100)])
    cpf = StringField('CPF', validators=[Optional(), Length(min=11, max=14)])
    birth_date = DateField('Data de Nascimento', validators=[Optional()])
    
    # Dados de Saúde (vão para a outra tabela)
    blood_type = SelectField('Tipo Sanguíneo', choices=[
        ('', 'Selecione'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), 
        ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    medical_notes = TextAreaField('Observações Médicas', validators=[Optional()])
    
    submit = SubmitField('Salvar Aluno')