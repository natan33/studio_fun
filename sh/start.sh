#!/bin/bash
# Script de inicialização do ambiente e serviços

# verifica se o arquivo requirements.txt foi modificado recentemente
REQUIREMENTS_FILE="requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    MODIFIED_TIME=$(stat -c %Y "$REQUIREMENTS_FILE")
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - MODIFIED_TIME))
    # se o arquivo foi modificado nos últimos 10 minutos (600 segundos), reinstala as dependências
    if [ $TIME_DIFF -lt 600 ]; then
        echo "Reinstalando dependências do pip..."
        # ativa o ambiente virtual
        if [ -z "$VIRTUAL_ENV" ]; then
            echo "Ativando ambiente virtual..."
            source ./venv/bin/activate
        else
            echo "Ambiente virtual já está ativado: $VIRTUAL_ENV"
        fi
        pip install -r requirements.txt
    fi
fi


# inicia o servidor Redis
echo "Iniciando Redis..."
sudo service redis-server start

# inicia o servidor Flask
echo "Iniciando servidor gunicorn."
export FLASK_APP=app
gunicorn --bind :5000 app:app

# remove as pastas __pycache__ para evitar conflitos
echo "Removendo pastas __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} +


# execução do Celery Worker para processamento de tarefas em segundo plano
echo "Iniciando Celery Worker..."
celery -A celery_worker.celery worker -P prefork --max-tasks-per-child=1000 --loglevel=info --detach

# execução do Celery Beat para agendamento de tarefas periódicas
echo "Iniciando Celery Beat..."
celery -A celery_worker.celery beat -l info --detach