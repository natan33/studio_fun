from flask_mail import Message
from flask import current_app
from celery_worker import celery # Sua instância do celery

@celery.task
def send_async_email(subject=None, recipient=None, body=None):
    """Tarefa assíncrona para enviar e-mail via Celery"""
    with current_app.app_context():
        from app import mail
        msg = Message(subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)