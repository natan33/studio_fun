from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length,NumberRange

class ActivityForm(FlaskForm):
    name = StringField('Nome da Atividade', validators=[
        DataRequired(), 
        Length(min=3, max=50, message="O nome deve ter entre 3 e 50 caracteres")
    ])
    description = TextAreaField('Descrição (Opcional)', validators=[Length(max=200)])
    submit = SubmitField('Cadastrar Atividade')


class ClassScheduleForm(FlaskForm):
    # O campo de atividade será preenchido dinamicamente no Controller
    activity_id = SelectField('Tipo de Aula', coerce=int, validators=[DataRequired()])
    
    day_of_week = SelectField('Dia da Semana', choices=[
        ('Segunda-feira', 'Segunda-feira'),
        ('Terça-feira', 'Terça-feira'),
        ('Quarta-feira', 'Quarta-feira'),
        ('Quinta-feira', 'Quinta-feira'),
        ('Sexta-feira', 'Sexta-feira'),
        ('Sábado', 'Sábado')
    ], validators=[DataRequired()])
    
    start_time = TimeField('Horário de Início', validators=[DataRequired()])
    
    max_capacity = IntegerField('Capacidade Máxima', default=15, validators=[
        DataRequired(), NumberRange(min=1, max=50)
    ])
    
    submit = SubmitField('Criar Turma')


class EnrollmentForm(FlaskForm):
    student_id = SelectField('Selecionar Aluno', coerce=int, validators=[DataRequired()])
    schedule_id = SelectField('Selecionar Turma', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Confirmar Matrícula')