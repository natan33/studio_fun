from flask import flash, render_template, request, redirect, url_for
from flask_login import current_user
from app.controllers.forms import LoginForm
from app.controllers.forms.form_auth import ForgotPasswordForm, ResetPasswordForm
from app.services.ServiceAuth import ServiceAutentication
from ..auth import auth # Assumindo que o logger já está configurado no seu __init__ ou logger.py
import random

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 

    from app.services import ServiceAutentication
    form = LoginForm()
    
    # Instancia o serviço
    auth_service = ServiceAutentication(request=request, forms=form)
    
    # Tenta a autenticação
    response = auth_service.autentication()
    
    # Se o serviço retornar um redirect (sucesso), a view obedece
    if response:
        return response

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    from app.services import ServiceAutentication
    auth_service = ServiceAutentication()
    return auth_service.logout()


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        response = ServiceAutentication.request_password_reset(form.email.data)
        
        # Agora acessamos como dicionário
        if response['code'] == 'SUCCESS':
            flash(response['message'], "success")
            # O primeiro argumento é 'blueprint.nome_da_funcao'
            return redirect(url_for('auth.reset_password', email=form.email.data))
        
        flash(response['message'], "danger")
        
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    
    # Se for o primeiro carregamento (GET), pegamos o email da query string e pomos no form
    if request.method == 'GET':
        form.email.data = request.args.get('email')

    if form.validate_on_submit():
        # Agora pegamos o email diretamente dos dados do formulário (POST)
        response = ServiceAutentication.reset_password(
            email=form.email.data, 
            code=form.code.data, 
            new_password_raw=form.password.data
        )
        
        if response['code'] == 'SUCCESS':
            flash(response['message'], "success")
            return redirect(url_for('auth.login'))
        
        flash(response['message'], "danger")

    return render_template('auth/reset_password.html', form=form)