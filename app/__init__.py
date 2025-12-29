import re
import logging
import time
import psutil
from datetime import timedelta
from collections import defaultdict 
from urllib.parse import urljoin, urlparse

from flask import Flask, redirect, render_template, request, session, url_for, jsonify
import requests
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_mail import Mail
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_session import Session
from flask_executor import Executor

# Imports internos
from app.core.config import config  # Importando o dicionário de instâncias
from app.tasks import make_celery
from app.utils.trace import register_trace_id
from app.utils.logger import setup_logger

# Instâncias das Extensões (Singleton Pattern)
db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CSRFProtect()
mail = Mail()
cache = Cache()
executor = Executor()
flask_session = Session()  # RENOMEADO para evitar conflito com flask.session
login_manager = LoginManager()

# Configuração do Login Manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

# Configura o Logger Global antes da criação do App
setup_logger()

def create_app(config_name: str):
    app = Flask(__name__)

    # Carrega a configuração do dicionário
    app.config.from_object(config[config_name])

    # Inicializa lógica personalizada da classe de config
    config[config_name].init_app(app)

    # Configuração de logging do Flask
    app.logger.setLevel(logging.INFO)

    # Inicialização das Extensões
    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    flask_session.init_app(app)  # Usando a instância renomeada
    executor.init_app(app)

    # Registro do user_loader para o Flask-Login
    from app.models.auth.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Inicializa o Celery
    celery = make_celery(app)

    # Middleware de Rastreabilidade (Trace ID)
    register_trace_id(app)

    # Registro de Blueprints
    from app.controllers.auth import auth as auth_blueprint
    from app.controllers.main import main as main_blueprint
    from app.controllers.api import api as api_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    return app