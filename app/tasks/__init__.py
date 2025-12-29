from celery import Celery
from app.core.config import Config

def make_celery(app):
    celery = Celery(app.import_name)
    config = Config()

    # CONFIGURAÇÕES NO NOVO PADRÃO
    
    celery.conf.update(
        broker_url=config.CELERY_BROKER_URL,
        result_backend=config.CELERY_RESULT_BACKEND,
        timezone="America/Sao_Paulo",
        enable_utc=True,
        
    )

    # PERMITE TASK(TAREFAS) COM CONTEXTO DO APP DO FLASK
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
