from app import create_app
from app.tasks import make_celery
from celery.schedules import crontab

app = create_app('development')
celery = make_celery(app)

# IMPORTAR TODAS TASKS
import app.tasks.finance_tasks
import app.tasks.finance_generate_task
# import app.tasks.uplaods_blob_task
# import app.tasks.uplaoder_google_driver
# import app.tasks.lote_views_task
# import app.tasks.marcar_inativos_task
# import app.tasks.notificacoes_task
celery.conf.beat_schedule = {
    'gerar-faturas-todo-mes': {
        'task': 'app.tasks.finance_tasks.generate_monthly_invoices_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=0), # Meia-noite do dia 1
    },
    'cleanup-pix-every-night': {
        'task': 'app.tasks.finance_tasks.cleanup_old_pix_files',
        'schedule': crontab(hour=3, minute=0), # Roda todo dia às 03:00 da manhã
    },
}

# celery.conf.beat_schedule = {
#     "marcar-usuarios-inativos-a-cada-5-min": {
#         "task": "app.tasks.marcar_inativos_task.marcar_usuarios_inativos",
#         "schedule": 300,
#     },
# }
