from app import db
from app.models.pages.academy import ClassSchedule
from app.utils.api_response import ApiResponse

class ActivitiesService:
    @staticmethod
    def toggle_activities_status(id_):
        try:
            activity = ClassSchedule.query.get(id_)
            if not activity:
                return False, "Aula não encontrada."

            # Lógica de alternância
            activity.status = 'Inativo' if activity.status == 'Ativo' else 'Ativo'
            
            db.session.commit()
            return True, f"Status alterado para {activity.status} com sucesso!"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar banco: {str(e)}"