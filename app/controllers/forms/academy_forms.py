from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ActivityForm(FlaskForm):
    name = StringField('Nome da Atividade', validators=[
        DataRequired(), 
        Length(min=3, max=50, message="O nome deve ter entre 3 e 50 caracteres")
    ])
    description = TextAreaField('Descrição (Opcional)', validators=[Length(max=200)])
    submit = SubmitField('Cadastrar Atividade')