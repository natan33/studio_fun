echo "Iniciando Redis..."
sudo service redis-server start

# 2️⃣ Ativa o ambiente virtual somente se não estiver ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Ativando ambiente virtual..."
    source ./venv/bin/activate
else
    echo "Ambiente virtual já está ativado: $VIRTUAL_ENV"
fi

echo "Iniciando Celery..."
celery -A celery_worker.celery worker -P prefork --max-tasks-per-child=1000 --loglevel=info