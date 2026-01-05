from app.utils.api_response import ApiResponse
from . import api
from flask_login import login_required, current_user
from app import db
from datetime import datetime, timezone


@api.route('/api/config/ping')
@login_required
@login_required
def user_ping():
    try:
        # Atualiza o timestamp de última atividade do usuário no banco
        current_user.last_seen = datetime.now()
        db.session.commit()
        
        # Retorna usando o seu padrão ApiResponse
        return ApiResponse.success(message="Atividade registrada")
    
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(str(e))