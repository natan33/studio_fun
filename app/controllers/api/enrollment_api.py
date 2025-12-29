
from app.services.enrollment_service import EnrollmentService
from . import api
from flask_login import login_required


@api.route('/api/enrollmente-dash', methods=['GET'])
@login_required
def get_enrollment_dashboard_data():
    service = EnrollmentService()
    return  service.get_enrollment_dashboard_data()

@api.route('/api/enrollment/enroll/<int:id>/lock', methods=['PATCH'])
@login_required
def lock_enrollment(id):
    service = EnrollmentService()
    return service.update_enrollment_status(id, 'Trancado')