from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Manter conectado')
    submit = SubmitField('Entrar')

class ForgotPasswordForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Código')

class ResetPasswordForm(FlaskForm):
    email = HiddenField()
    code = StringField('Código de Recuperação', validators=[DataRequired()])
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    submit = SubmitField('Redefinir Senha')