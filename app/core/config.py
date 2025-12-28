from collections import namedtuple
import os
from datetime import timedelta
from pathlib import Path
import socket
import json
from dotenv import load_dotenv


Setup = namedtuple('Setup', [ 'config'])


def read_():
    file_path = fr"{Path(os.getcwd()) / '.cred_api.json' }"
    with open(file_path, mode="r+", encoding="utf-8") as r:
            return json.load(r)
    
class BaseConfig:
    """Configuração Base com lógica de detecção de ambiente."""
    
    def __init__(self):
        # Resolve o diretório raiz (ajuste o número de .parent conforme sua estrutura)
        self.BASE_DIR = Path(__file__).resolve().parent
        
        # Detecta ambiente
        self.FLASK_ENV = os.getenv("FLASK_ENV", "development").lower()
        self.IS_PRODUCTION = self.FLASK_ENV == "production"

        self._load_and_validate()

    def _load_and_validate(self):
        env_file = self.BASE_DIR / '.env'
        
        if not self.IS_PRODUCTION:
            if env_file.exists():
                load_dotenv(env_file)
                #print(f"[*] Modo {self.FLASK_ENV.upper()}: .env carregado.")
            else:
                print(f"⚠️  Aviso: .env não encontrado em {self.BASE_DIR}")
        else:
            # Proteção Hardened: Impede execução se houver arquivo físico de segredos
            if env_file.exists():
                raise RuntimeError(
                    "❌ VIOLAÇÃO DE SEGURANÇA: Arquivo .env detectado em PRODUÇÃO. "
                    "Remova o arquivo e use variáveis de ambiente do Sistema/Container."
                )

    @staticmethod
    def get_env_or_raise(var_name: str) -> str:
        """Garante que variáveis críticas existam no SO."""
        value = os.getenv(var_name)
        if not value:
            raise RuntimeError(f"❌ Variável obrigatória ausente: {var_name}")
        return value
    

class ConfiGrafh(BaseConfig):

    def __init__(self):

        super().__init__()
        
        # Application (client) ID of app registration
        self.CLIENT_ID = self.get_env_or_raise('CLIENT_ID')
    
        # Application's generated client secret: never check this into source control!
        self.LOGIN_MICROSOFT = self.get_env_or_raise('LOGIN_MICROSOFT')
    
        self.CLIENT_SECRET = self.get_env_or_raise('CLIENT_SECRET')
    
        self.B2C_TENANT_NAME=self.get_env_or_raise('B2C_TENANT_NAME')
        self.SIGNUPSIGNIN_USER_FLOW=self.get_env_or_raise('SIGNUPSIGNIN_USER_FLOW')
        self.EDITPROFILE_USER_FLOW=self.get_env_or_raise('EDITPROFILE_USER_FLOW')
        self.RESETPASSWORD_USER_FLOW=self.get_env_or_raise('RESETPASSWORD_USER_FLOW')
    
        self.TENANT_ID = self.get_env_or_raise('TENANT_ID')    
    
        self.AUTHORITY = fr"{self.get_env_or_raise('AUTHORITY')}{self.TENANT_ID}"

        self.REDIRECT_PATH = self.verifica_host()
        #"https://ideal.fgb.com.br/getAToken" # COMENTAR PARA DESENVOLVER LOCALMENTE
        # The absolute URL must match the redirect URI you set
        # in the app's registration in the Azure portal.
    
        # You can find more Microsoft Graph API endpoints from Graph Explorer
        # https://developer.microsoft.com/en-us/graph/graph-explorer
        self.ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent
    
        # You can find the proper permission names from this document
        # https://docs.microsoft.com/en-us/graph/permissions-reference
        self.SCOPE = ["User.ReadBasic.All"]
    
        # Tells the Flask-session extension to store sessions in the filesystem
        self.SESSION_TYPE = "filesystem"
    

    def verifica_host(self):
        nome_host = socket.gethostname()
        ip_local = socket.gethostbyname(nome_host)

        print(ip_local)

        if (
            ip_local.startswith(self.get_env_or_raise("LOCAL_IP_PREFIX_1")) or
            ip_local.startswith(self.get_env_or_raise("LOCAL_IP_PREFIX_2")) or
            ip_local.startswith(self.get_env_or_raise("LOCAL_IP_1")) or
            ip_local.startswith(self.get_env_or_raise("LOCAL_IP_2")) or
            ip_local.startswith(self.get_env_or_raise("LOCAL_IP_3")) or
            ip_local == self.get_env_or_raise("LOCAL_IP_LOOPBACK")
        ):
            return self.get_env_or_raise("LOCAL_TOKEN_URL")

        elif ip_local.startswith(self.get_env_or_raise("PROD_IP")):
            return self.get_env_or_raise("PROD_TOKEN_URL")

        elif ip_local.startswith(self.get_env_or_raise("INTERNAL_IP")):
            return self.get_env_or_raise("INTERNAL_TOKEN_URL")




 
class Config(BaseConfig):

    def __init__(self):
        super().__init__()

        self.SECRET_KEY = self.get_env_or_raise('SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = self.get_env_or_raise('SQLALCHEMY_DATABASE_URI')
        self.CELERY_BROKER_URL = self.get_env_or_raise('CELERY_BROKER_URL')
        self.CELERY_RESULT_BACKEND = self.get_env_or_raise('CELERY_RESULT_BACKEND')
        self.VM_PASSWORD = self.get_env_or_raise('VM_PASS')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.MAX_CONTENT_LENGTH = 10 * 1024 * 1024
        self.DROPZONE_ALLOWED_FILE_CUSTOM = True
        self.DROPZONE_ALLOWED_FILE_TYPE = '.pdf, .txt, .xlsx, .jpg, .docx, .msg, .rar, .zip, .ppt, .pptx'
        self.DROPZONE_MAX_FILE_SIZE = 10 * 1024 * 1024
        self.DROPZONE_TIMEOUT = 5 * 60 * 1000
        self.DROPZONE_DEFAULT_MESSAGE = "Solte seus arquivos aqui ou clique para enviar."
        self.DROPZONE_INVALID_FILE_TYPE = "Você não pode enviar arquivos deste tipo."
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
        self.SESSION_PERMANENT = False
        self.SESSION_COOKIE_SECURE = True
        self.CACHE_TYPE = 'simple'
        self.CACHE_DEFAULT_TIMEOUT = 300
        self.ALLOWED_HOSTS = {
            # self.get_env_or_raise("IP_ALLOWED_PROD_URL"),
            # self.get_env_or_raise("IP_ALLOWED_1"),
            # self.get_env_or_raise("IP_ALLOWED_2"),
            # self.get_env_or_raise("IP_ALLOWED_3"),
            # self.get_env_or_raise("IP_ALLOWED_4"),
            # self.get_env_or_raise("IP_ALLOWED_5"),
            # self.get_env_or_raise("IP_ALLOWED_6")    
        }
        self.ACESS_TOKEN_SEND_EMAIL = self.get_env_or_raise('ACESS_TOKEN_SEND_EMAIL')
        self.MAIL_PORT=self.get_env_or_raise('MAIL_PORT')
        self.MAIL_USE_TLS=self.get_env_or_raise('MAIL_USE_TLS')
        self.MAIL_USERNAME=self.get_env_or_raise('MAIL_USERNAME')
        self.MAIL_PASSWORD=self.get_env_or_raise('MAIL_PASSWORD')
        self.TOKEN_SECRET_SOCKET = self.get_env_or_raise('TOKEN_SECRET_SOCKET')
        self.LINK_SOCKET_SERVER=self.get_env_or_raise('LINK_SOCKET_SERVER')
        self.API_SOCKET_HEADERS = {"Authorization": f"Bearer {self.get_env_or_raise('API_SOCKET_HEADERS')}"}

        self.MAX_CONTENT_LENGTH = 500 * 1000 * 1000
        self.SESSION_TYPE = "filesystem"
        self.SESSION_PERMANENT = False  # Habilitar sessões permanentes
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        self.SESSION_USE_SIGNER = True
        # Apenas para ambiente local
        self.SESSION_COOKIE_SECURE = False
        self.SESSION_COOKIE_SAMESITE = 'Lax'

        # FLASK_EXECUTOR
        self.CUSTOM_EXECUTOR_TYPE = 'thread'
        self.CUSTOM_EXECUTOR_MAX_WORKERS = 5

    
    @staticmethod
    def init_app(app):
        print("Initializing application!")
        pass
 
 
class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()

        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = self.get_env_or_raise('SQLALCHEMY_DATABASE_URI')
        self.DB_USER = self.get_env_or_raise('DB_USER')
        self.DB_PASSWORD = self.get_env_or_raise('DB_PASSWORD')
        self.DB_HOST = self.get_env_or_raise('DB_HOST')
        self.DB_PORT = self.get_env_or_raise('DB_PORT')
        self.DB_NAME = self.get_env_or_raise('DB_NAME')
        self.TESTING = False

        self.UPLOAD_FOLDER = os.path.abspath('app/uploads')
        self.DOWNLOAD_LOG = os.path.abspath('app/static/downloads/logs')
        self.ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'xls', 'doc', 'docx', 'zip', 'msg', 'csv', 'rar', 'ppt', 'pptx'}
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024

        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
        self.MAIL_SERVER = self.get_env_or_raise('MAIL_SERVER')
        self.MAIL_PORT =self.get_env_or_raise('MAIL_PORT')
        self.MAIL_USE_TLS = self.get_env_or_raise('MAIL_USE_TLS')
        self.MAIL_USERNAME = self.get_env_or_raise('MAIL_USERNAME')
        self.MAIL_PASSWORD = self.get_env_or_raise('MAIL_PASSWORD')
        self.MAIL_DEFAULT_SENDER = self.get_env_or_raise('MAIL_USERNAME')
 
 
class TestingConfig(Config):  #ambient of testing
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/postgres'
        self.DB_USER = 'postgres'
        self.DB_PASSWORD = 'postgres'
        self.DB_HOST = 'localhost'
        self.DB_PORT = '5432'
        self.DB_NAME = 'postgres'
        self.GLO_OB = ''
        self.UPLOAD_FOLDER = os.path.abspath('app/uploads')
        self.DOWNLOAD_LOG = os.path.abspath('app/static/downloads/logs')
        self.ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'xls', 'doc', 'docx', 'zip', 'msg', 'rar', 'ppt', 'pptx'}
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024
        self.PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
        self.CACHE_TYPE = 'simple'
        self.CACHE_DEFAULT_TIMEOUT = 300
 
 
class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.TESTING = False

        self.SQLALCHEMY_DATABASE_URI = self.get_env_or_raise("SQLALCHEMY_DATABASE_URI")

        self.DB_USER = self.get_env_or_raise("DB_USER")
        self.DB_PASSWORD = self.get_env_or_raise("DB_PASSWORD")
        self.DB_HOST = self.get_env_or_raise("DB_HOST")
        self.DB_PORT = self.get_env_or_raise("DB_PORT")
        self.DB_NAME = self.get_env_or_raise("DB_NAME")

        self.MAIL_USERNAME = self.get_env_or_raise("MAIL_USERNAME")
        self.MAIL_PASSWORD = self.get_env_or_raise("MAIL_PASSWORD")

        self.UPLOAD_FOLDER = os.path.abspath("app/uploads")
        self.DOWNLOAD_LOG = os.path.abspath("app/static/downloads/logs")

class ConfigSocket(BaseConfig):
    def __init__(self):
        super().__init__()
        self.cors_allowed_origins = self.get_env_or_raise('CORS_ALLOWED_ORIGINS')
        self.async_mode = self.get_env_or_raise('ASYNC_MODE')
        self.message_queue = self.get_env_or_raise('MESSAGE_QUEUE')  # corrigido typo


 
 
# Chave para inicilizacao das config no init
config = {
    'development': DevelopmentConfig(), # <--- Note os parênteses
    'testing': TestingConfig(),     # <--- Note os parênteses
    'production': ProductionConfig(),   # <--- Note os parênteses
    'default': DevelopmentConfig()
}
# setup =ConfiGrafh()

# setup_run_time = Setup(
#     config=ConfigSocket()
# )
