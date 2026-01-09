from app.services.DashboardService import DashboardService
from app.utils.api_response import ApiResponse
from . import api


@api.route('/api/dashboad/top-occupancy')
def api_dashboad_top_occupancy():
    service = DashboardService()
    data = service.get_tbl_dashboard()
    return ApiResponse.success(data=data)

@api.route('/api/dashboard/cards')
def api_dashboard_cards():
    service = DashboardService()
    return service.get_dashboard_cards()