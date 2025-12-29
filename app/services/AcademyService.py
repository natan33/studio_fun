from app import db
from app.models.pages.academy import Activity
from app.utils.api_response import ApiResponse
import logging

logger = logging.getLogger(__name__)

class AcademyService:
    def __init__(self, form=None, request=None):
        self.form = form
        self.request = request

    def create_activity(self):
        """Cria um novo tipo de aula (Zumba, Funcional, etc)"""
        if not self.form or not self.form.validate_on_submit():
            errors = {field: err[0] for field, err in self.form.errors.items()}
            return ApiResponse.error(message="Erro de validação", data=errors)

        try:
            # Verifica se já existe uma atividade com esse nome
            name_upper = self.form.name.data.upper()
            exists = Activity.query.filter(Activity.name.ilike(name_upper)).first()
            if exists:
                return ApiResponse.error(message="Esta atividade já está cadastrada.")

            new_activity = Activity(
                name=self.form.name.data,
                description=self.form.description.data
            )
            db.session.add(new_activity)
            db.session.commit()
            
            logger.info(f"Nova atividade criada: {new_activity.name}")
            return ApiResponse.success(message="Tipo de aula cadastrado com sucesso!")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar atividade: {str(e)}")
            return ApiResponse.error(message="Erro interno ao salvar atividade.")

    def list_activities(self):
        """Retorna a lista de atividades para a tabela"""
        return Activity.query.order_by(Activity.name).all()