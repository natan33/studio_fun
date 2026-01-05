from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ExpenseForm(FlaskForm):
    type_form = HiddenField('type_form')
    expense_id = HiddenField('expense_id')
    description = StringField('Descrição', validators=[DataRequired()])
    category = SelectField('Categoria', choices=[
        ('Fixo', 'Fixo (Aluguel, Internet)'),
        ('Variavel', 'Variável (Manutenção)'),
        ('Pessoal', 'Pessoal (Salários)'),
        ('Marketing', 'Marketing/Anúncios'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    amount = DecimalField('Valor', places=2, validators=[DataRequired()])
    due_date = DateField('Vencimento', validators=[DataRequired()])
    submit = SubmitField('Salvar Despesa')