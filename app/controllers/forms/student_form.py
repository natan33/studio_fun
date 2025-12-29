from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, DateField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length

class StudentForm(FlaskForm):
    student_id = HiddenField('student_id')
    # --- Dados Pessoais ---
    full_name = StringField('Nome Completo', validators=[
        DataRequired(message="O nome é obrigatório."),
        Length(min=3, max=100)
    ])
    cpf = StringField('CPF', validators=[
        DataRequired(message="O CPF é obrigatório."),
        Length(min=11, max=14)
    ])
    email = StringField('E-mail', validators=[
        Optional(),
        Email(message="E-mail inválido."),
        Length(max=120)
    ])
    phone = StringField('Telefone', validators=[
        Optional(),
        Length(max=20)
    ])
    birth_date = DateField('Data de Nascimento',format='%Y-%m-%d', validators=[
        DataRequired(message="A data de nascimento é obrigatória.")
    ])

    # --- Endereço ---
    postal_code = StringField('CEP', validators=[Optional(), Length(max=10)])
    address = StringField('Logradouro', validators=[Optional(), Length(max=150)])
    address_number = StringField('Número', validators=[Optional(), Length(max=10)])
    city = StringField('Cidade', validators=[Optional(), Length(max=50)])

    # --- Saúde (StudentHealth) ---
    blood_type = SelectField('Tipo Sanguíneo', choices=[
        ('', 'Selecione...'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    
    weight = FloatField('Peso (kg)', validators=[Optional()])
    height = FloatField('Altura (m)', validators=[Optional()])
    medical_notes = TextAreaField('Observações Médicas', validators=[Optional()])

    # --- Emergência ---
    emergency_contact = StringField('Contato de Emergência', validators=[Optional(), Length(max=100)])
    emergency_phone = StringField('Telefone de Emergência', validators=[Optional(), Length(max=20)])