from app.services import ActivitiesService
from app.utils.api_response import ApiResponse
from . import api
from flask_login import login_required


@api.route('/api/activities/<int:id>/toggle-status', methods=['POST', 'PATCH'])
@login_required
def toggle_activities_status(id):
    try:
        # Chama o service (que agora faz o toggle do campo status)
        success, message = ActivitiesService.toggle_activities_status(id)
        
        if success:
            return ApiResponse.success(message=message)
        else:
            return ApiResponse.error(message=message)
            
    except Exception as e:
        # Logar o erro real no console para debug
        print(f"Erro na rota: {e}") 
        return ApiResponse.error(message="Erro interno ao processar a aula.")