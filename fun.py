from app.core.factory import create_app, db
from app.models import User, Registration
from flask_migrate import Migrate


# Define o ambiente desejado: 'development', 'testing' ou 'production'
env = 'development'  # Altere o tipo de ambiente para development, testing ou production

app = create_app(env)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
   return dict(db=db, User=User, Registration=Registration)
