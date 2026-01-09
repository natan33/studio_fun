#!/bin/bash

# Cores
CYAN='\033[0;36m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

start() {
    echo -e "${CYAN}🚀 Iniciando Ecossistema Studio Fun...${NC}"

    # 1. Limpeza de Cache do Python
    echo -e "${YELLOW}🧹 Limpando arquivos compilados (__pycache__)...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

    # 2. Garantir que o Redis está rodando
    echo -e "${YELLOW}🔄 Verificando Redis Server...${NC}"
    sudo service redis-server start

    # 3. Ativa venv
    source ./venv/bin/activate

    # 4. Inicia o Socket em segundo plano (via notify.sh)
    echo -e "${CYAN}💻 Subindo App Principal (Porta 5000)...${NC}"
    export FLASK_APP=fun.py
    ./sh/start.sh start

}

stop() {
    echo -e "${RED}🛑 Derrubando todo o ecossistema...${NC}"
    ./sh/notify.sh stop
    fuser -k 5000/tcp > /dev/null 2>&1
    echo -e "${GREEN}✅ Tudo desligado.${NC}"
}
celery_run() {
    # 1. Ativa venv
    source ./venv/bin/activate
    # 2. Inicia o celery
    echo -e "${CYAN}🚀 Iniciando ecossistema do Celery...${NC}"
    celery -A celery_worker.celery worker -P prefork --max-tasks-per-child=1000 --loglevel=info
    
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|}"
        exit 1
esac