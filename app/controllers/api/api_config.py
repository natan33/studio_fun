from . import api
from flask_login import login_required, current_user
from app import db
from datetime import datetime, timezone


@api.route('/api/config/ping')
@login_required
def api_config_ping():
    """Rota de teste para verificar se a API está respondendo"""
    current_user.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    return '', 204