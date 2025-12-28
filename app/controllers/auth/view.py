from flask import render_template, request, redirect, url_for
from flask_login import current_user
from app.controllers.forms import LoginForm
from ..auth import auth # Assumindo que o logger já está configurado no seu __init__ ou logger.py

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