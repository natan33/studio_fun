from flask import flash, redirect, url_for
from flask_login import login_user, logout_user
from app.models.auth.user import User
import logging

# Este logger usará o TraceIdFilter definido no seu setup_logger
logger = logging.getLogger(__name__)

class ServiceAutentication:
    def __init__(self, request=None, forms=None):
        self.request = request
        self.form = forms

    def autentication(self):
        # Verifica se o formulário foi submetido e é válido (CSRF incluso aqui)
        if self.form and self.form.validate_on_submit():
            user = User.query.filter_by(email=self.form.email.data).first()

            if user and user.check_password(self.form.password.data):
                # Flask-Login + Redis Session
                login_user(user, remember=self.form.remember_me.data)
                
                logger.info(f"Usuário {user.email} logado via sessão.")
                
                # Busca o parâmetro 'next' para redirecionar após o login
                next_page = self.request.args.get('next')
                return redirect(next_page or url_for('main.index'))
            
            # Caso falhe a senha ou usuário
            logger.warning(f"Falha de login para o email: {self.form.email.data}")
            flash('E-mail ou senha inválidos.', 'danger')
        
        return None # Se não validou ou é GET, retorna None

    def logout(self):
        logout_user()
        logger.info("Usuário realizou logout.")
        return redirect(url_for('auth.login'))