from app import db
from app.models.pages.academy import Schedule
from app.utils.api_response import ApiResponse

class ActivitiesService:
    @staticmethod
    def delete_activities(id_):
        try:
            # Busca a aula (Schedule) pelo ID
            activity = Schedule.query.get(id_)
            
            if not activity:
                return False, "Aula não encontrada."

            db.session.delete(activity)
            db.session.commit()
            return True, "Aula excluída com sucesso!"
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir aula: {e}")
            return False, f"Erro ao excluir: {str(e)}"