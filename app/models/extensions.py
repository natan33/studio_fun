from datetime import datetime
from app import db # ajuste conforme seu projeto
from flask_login import current_user

class AuditMixin:
    last_modified_by = db.Column(db.String(50), nullable=True)

    def update_audit(self):
        # Import local para evitar importação circular
        from flask_login import current_user
        try:
            # is_authenticated garante que não estamos tentando pegar o username do AnonymousUser
            if current_user and current_user.is_authenticated:
                self.last_modified_by = current_user.username
            else:
                self.last_modified_by = "system"
        except Exception:
            self.last_modified_by = "system"