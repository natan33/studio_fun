
from flask import request
from app.models.pages.students import Student
from app.services.enrollment_service import EnrollmentService
from app.utils.api_response import ApiResponse
from . import api
from flask_login import login_required


@api.route('/api/enrollments', methods=['GET'])
@login_required
def get_enrollments():
    service = EnrollmentService()
    return service.list_enrollments()    

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

@api.route('/api/enrollments/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_enrollment_status(id):
    service = EnrollmentService()
    return service.toggle_enrollment_status(id, "Ativo")


@api.route('/api/enrollments/<int:id>/delete', methods=['DELETE', 'POST'])
@login_required
def delete_enrollment(id):
    try:
        # Utilizamos o service para lidar com a lógica de exclusão e banco de dados
        success, message = EnrollmentService.delete_enrollment(id)
        
        if success:
            return ApiResponse.success(message=message)
        else:
            return ApiResponse.error(message=message)
            
    except Exception as e:
        print(f"Erro na rota de exclusão: {e}")
        return ApiResponse.error(message="Erro interno ao processar a exclusão.")
    

@api.route('/api/enrollments/get-students', methods=['GET'])
@login_required
def get_enrollments_students():

    service = EnrollmentService(request=request)
    return service.get_students()

@api.route('/api/enrollments/get-schedules',methods=['GET'])
@login_required
def get_enrollments_schedules():

    service = EnrollmentService(request=request)
    return service.get_schedules()
