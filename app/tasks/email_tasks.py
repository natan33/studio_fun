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
        
@celery.task(name="send_async_invoice")
def send_async_invoice(subject, recipient, template, data):
    with current_app.app_context():
        from app import mail
        msg = Message(subject, recipients=[recipient])
        # Renderiza o template passando o dicionário de dados descompactado
        msg.html = render_template(template, **data)
        
        try:
            mail.send(msg)
            return f"E-mail enviado para {recipient}"
        except Exception as e:
            return f"Erro no envio: {str(e)}"
        

@celery.task(name='tasks.send_welcome_email')
def send_welcome_email(student_email=None, student_name=None, plan_name=None, class_name=None, schedule=None, enrollment_date=None, student_id=None):
    # Usamos o current_app dentro do context para o Jinja2 e o Mail funcionarem
    with current_app.app_context():
        try:
            # Importação interna do objeto mail para evitar imports circulares
            from app import mail,db
            from app.models import WelcomeEmailLog
            from flask_mail import Message
            
            subject = f"Bem-vindo ao Studio Fun, {student_name}! 🚀"
            
            # Criando a mensagem
            msg = Message(
                subject=subject,
                recipients=[student_email]
                # Caso queira enviar uma cópia oculta para o admin do sistema:
                # bcc=["contato@studiofun.com.br"] 
            )
            
            # Renderizando o HTML da sua pasta templates/emails
            msg.html = render_template(
                'emails/welcome_student.html',
                student_name=student_name,
                plan_name=plan_name,
                class_name=class_name,
                schedule=schedule,
                enrollment_date=enrollment_date
            )
            
            # Envio definitivo
            mail.send(msg)
            
            print(f"✅ LOG: E-mail de boas-vindas enviado para {student_email}")


            log = WelcomeEmailLog(student_id=student_id)
            db.session.add(log)
            db.session.commit()

            return f"Sucesso: {student_email}"
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ LOG: Erro ao enviar para {student_email}: {str(e)}")
            return f"Erro: {str(e)}"