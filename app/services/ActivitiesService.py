from venv import logger
from app import db
from app.models.pages.academy import ClassSchedule
from app.utils.api_response import ApiResponse

from app.models.pages.academy import Activity # Importe Activity aqui

class ActivitiesService:

    def __init__(self, form=None, request=None):
        self.form = form
        self.request = request

    
    def main_form(self):

            if self.form.validate_on_submit():
                # Captura o ID do campo oculto
                id_atividade = self.form.activity_id.data
                
            if id_atividade:
                # Se tem ID, dispara a def de EDITAR
                update_activity = self.update_activity(
                    id_=id_atividade, 
                    name=self.form.name.data, 
                    description=self.form.description.data
                )
                return update_activity
            else:
                # Se NÃO tem ID, dispara a def de CRIAR
                create_activity = self.create_activity()
                return create_activity

    @staticmethod
    def toggle_activities_status(id_):
        try:
            # Buscamos Activity, que é o que você lista no HTML
            activity = Activity.query.get(id_)
            
            if not activity:
                return False, "Atividade não encontrada."

            # Toggle robusto
            if not activity.status or activity.status == 'Ativo':
                activity.status = 'Inativo'
            else:
                activity.status = 'Ativo'
            
            db.session.commit()
            return True, f"Atividade agora está {activity.status}!"
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @staticmethod
    def list_all( as_dict=False):
        """Retorna todas as atividades. Se as_dict for True, retorna para JSON."""
        activities = Activity.query.order_by(Activity.name).all()
        
        if as_dict:
            return [s.to_dict() for s in activities]

        return activities # Retorna a lista de objetos para o Jinj # Exemplo se tiver to_dict
    
    def update_activity(self,id_=None, name=None, description=None):
        try:
            activity = Activity.query.get(id_)
            if not activity:
                return ApiResponse.error(message="Atividade não encontrada.")
            
            activity.name = name
            activity.description = description
            db.session.commit()
            return ApiResponse.success(message="Atividade atualizada com sucesso!")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar atividade: {str(e)}")
            return ApiResponse.error(message="Erro interno ao Atualizar a atividade.")

        
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
