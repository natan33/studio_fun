from app.controllers.forms.academy_forms import ActivityForm
from app.models.pages.academy import Activity
from app.services.ActivitiesService import ActivitiesService
from app.utils.api_response import ApiResponse
from . import api
from app import db
from flask_login import login_required


@api.route('/api/activities/list', methods=['GET'])
@login_required
def list_activities_json():
    try:
        # Convertemos a lista de objetos para lista de dicionários
        data = ActivitiesService.list_all(as_dict=True)
        
        # Usamos o ApiResponse.success enviando os dados no parâmetro 'data'
        return ApiResponse.success(data=data)
    except Exception as e:
        print(f"Erro ao listar atividades: {e}")
        return ApiResponse.error(message="Erro ao carregar lista de atividades.")

@api.route('/api/activities/<int:id>/toggle-status', methods=['POST', 'PATCH'])
@login_required
def toggle_activities_status(id):
    try:
        # Chama o service
        success, message = ActivitiesService.toggle_activities_status(id)
        
        if success:
            return ApiResponse.success(message=message)
        else:
            return ApiResponse.error(message=message)
            
    except Exception as e:
        db.session.rollback() # Segurança para manter a sessão limpa
        print(f"Erro na rota toggle-status: {e}") 
        return ApiResponse.error(message="Erro interno ao processar a requisição.")
    
# Rota para buscar dados de UMA atividade
@api.route('/api/activities/<int:id>', methods=['GET'])
@login_required
def get_activity(id):
    activity = Activity.query.get_or_404(id)
    return ApiResponse.success(data=activity.to_dict())

# Rota para atualizar
@api.route('/api/activities/<int:id>/update', methods=['POST'])
@login_required
def update_activity(id):
    form = ActivityForm()
    if form.validate_on_submit():
        success, message = ActivitiesService.update_activity(id, form.name.data, form.description.data)
        return ApiResponse.success(message=message) if success else ApiResponse.error(message=message)
    return ApiResponse.error(message="Dados inválidos.")