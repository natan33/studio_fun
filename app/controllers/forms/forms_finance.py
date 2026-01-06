
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange,Optional

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


class PlanForm(FlaskForm):
    plan_id = SelectField('Selecionar Plano', coerce=int, validators=[Optional()])
    name = StringField('Nome do Plano', validators=[Optional()])
    
    price = DecimalField('Preço (R$)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    
    # Deixamos as escolhas aqui para o Flask reconhecer a validação
    duration_months = SelectField('Duração', coerce=int, default=1, choices=[
        (7, 'Quinzenal (15 dias)'),
        (1, 'Mensal (1 mês)'),
        (2, 'Bimestral (2 meses)'),
        (3, 'Trimestral (3 meses)'),
        (4, 'Quadrimestral (4 meses)'),
        (5, 'Quinquenal (5 meses)'),
        (6, 'Semestral (6 meses)'),
        (12, 'Anual (12 meses)')
    ])

class PaymentTypeForm(FlaskForm):
    tp_pag = SelectField("Tipo de Pagamento", validators=[DataRequired()],choices=[
        ('Dinheiro', 'Dinheiro'),
        ('Cartão de Crédito', 'Cartão de Crédito'),
        ('Cartão de Débito', 'Cartão de Débito'),
        ('Transferência Bancária', 'Transferência Bancária'),
        ('PIX', 'PIX'),
        ('Cheque', 'Cheque'),
        ('Boleto Bancário', 'Boleto Bancário')
    ])
    description = StringField('Descrição (Opcional)', validators=[Optional()])
    submit = SubmitField('Salvar Tipo de Pagamento')