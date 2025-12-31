from app.services import ActivitiesService
from app.utils.api_response import ApiResponse
from . import api
from flask_login import login_required


@api.route('/api/activities/<int:id>/delete', methods=['DELETE', 'POST'])
@login_required
def delete_activity(id):
    try:
        # Chama o service
        success, message = ActivitiesService.delete_activities(id)
        
        if success:
            return ApiResponse.success(message=message)
        else:
            return ApiResponse.error(message=message)
            
    except Exception as e:
        return ApiResponse.error(message="Erro interno ao processar a exclusão da aula.")