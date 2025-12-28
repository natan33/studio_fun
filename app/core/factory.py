import re
from urllib.parse import urljoin, urlparse
from flask import Flask, redirect, render_template, request, session, url_for,jsonify
import requests
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_required
from flask_mail import Mail
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from app.core.config import *
import logging
from datetime import timedelta
from collections import defaultdict 
import time
import psutil # Para monitoramento de CPU/Memória
 
from flask_session import Session
from flask_executor import Executor

from app.tasks import make_celery

from app.utils.trace import register_trace_id
from app.utils.logger import setup_logger

# Defina as rotas a serem excluídas do monitoramento em uma tupla
 
db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CSRFProtect()
mail = Mail()
cache = Cache()
executor = Executor()
session = Session()
 
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

setup_logger()

def create_app(config_name:str):
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    # Configuração de logging
    app.logger.setLevel(logging.INFO)

    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    session.init_app(app)
    executor.init_app(app)

    # Inicializa o Celery com a app
    celery = make_celery(app)


    register_trace_id(app)

    from app.controllers.auth import auth as auth_blueprint
    from app.controllers.main import main as main_blueprint
    from app.controllers.api import api as api_blueprint
 
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

 
    return app