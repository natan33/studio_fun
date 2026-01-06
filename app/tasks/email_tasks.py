from flask_mail import Message
from flask import current_app, render_template
from celery_worker import celery # Sua instância do celery

@celery.task(bind=True)
def send_async_email(self, subject=None, recipient=None, template_data=None):
    """Tarefa assíncrona para enviar e-mail via Celery"""
    """
    template_data deve ser um dicionário com:
    {'username': '...', 'code': '...', 'template': 'emails/reset_password.html'}
    """
    with current_app.app_context():
        from app import mail
        msg = Message(
            subject,
            recipients=[recipient]
        )
        # Renderiza o HTML com os dados do usuário
        msg.html = render_template(
            template_data['template'], 
            username=template_data['username'], 
            code=template_data['code']
        )
        
        try:
            mail.send(msg)
            return f"E-mail HTML enviado para {recipient}"
        except Exception as e:
            return f"Erro: {str(e)}"