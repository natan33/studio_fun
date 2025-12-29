from app import db
from app.models import *
from app.utils.api_response import ApiResponse


class EnrollmentService:
    def __init__(self,forms=None,request=None):
        self.form = forms
        self.request=request

    def get_enrollment_dashboard_data(self):
            try:
                from app.models.pages.academy import Enrollment, Attendance

                enrollments = Enrollment.query.all()
                
                # 1. Contagem por Status
                total = len(enrollments)
                ativos = len([e for e in enrollments if e.status == 'Ativo'])
                trancados = len([e for e in enrollments if e.status == 'Trancado'])

                # 2. Lógica de Frequência Média
                total_presencas = Attendance.query.count()
                freq_media = 0
                if total > 0 and total_presencas > 0:
                    freq_media = round((total_presencas / (total * 12)) * 100, 1)

                # O SEGREDO: Envie apenas os números (stats), não os objetos do banco
                data = {
                    "total": total,
                    "ativos": ativos,
                    "trancados": trancados,
                    "freq_media": f"{freq_media}%" if freq_media > 0 else "---"
                }
            
                return ApiResponse.success(data=data)
            except Exception as e:
                print(f"Erro no Service: {e}")
                return ApiResponse.error(message=str(e))
            
    def update_enrollment_status(self, enrollment_id=None, new_status=None):
            try:
                from app.models.pages.academy import Enrollment
                
                enrollment = Enrollment.query.get(enrollment_id)
                
                if not enrollment:
                    return ApiResponse.error(message="Matrícula não encontrada.")
                
                # Atualiza apenas o status
                enrollment.status = new_status
                db.session.commit()
                
                return ApiResponse.success(message=f"Matrícula alterada para {new_status}!")
                
            except Exception as e:
                db.session.rollback()
                print(e)
                return ApiResponse.error(message=str(e))