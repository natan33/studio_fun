from app import create_app
from app.tasks import make_celery

app = create_app('development')
celery = make_celery(app)

# IMPORTAR TODAS TASKS
# import app.tasks.excel_task
# import app.tasks.uplaods_blob_task
# import app.tasks.uplaoder_google_driver
# import app.tasks.lote_views_task
# import app.tasks.marcar_inativos_task
# import app.tasks.notificacoes_task

# celery.conf.beat_schedule = {
#     "marcar-usuarios-inativos-a-cada-5-min": {
#         "task": "app.tasks.marcar_inativos_task.marcar_usuarios_inativos",
#         "schedule": 300,
#     },
# }
