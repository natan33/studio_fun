from app import db
from sqlalchemy.exc import IntegrityError
from app.models.pages.students import Student, StudentHealth
from app.utils.api_response import ApiResponse # Supondo que o caminho seja esse
import logging

logger = logging.getLogger(__name__)

class StudentService:

    def __init__(self, request=None, forms=None):
        self.request = request
        self.form = forms

    def create_student(self):
        """Lógica de negócio para criação de aluno com retorno padronizado"""
        
        # 1. Validação do formulário
        if not self.form or not self.form.validate_on_submit():
            # Se o form for inválido, extraímos os erros para o SweetAlert mostrar
            errors = {field: err[0] for field, err in self.form.errors.items()}
            return ApiResponse.error(message="Erro de validação", data=errors)

        try:
            # 2. Instância do Aluno
            new_student = Student(
                full_name=self.form.full_name.data,
                cpf=self.form.cpf.data,
                birth_date=self.form.birth_date.data
            )
            db.session.add(new_student)
            
            # Flush para obter o ID sem fechar a transação
            db.session.flush()

            # 3. Instância dos Dados de Saúde
            health_info = StudentHealth(
                student_id=new_student.id,
                blood_type=self.form.blood_type.data,
                weight=self.form.weight.data,
                medical_notes=self.form.medical_notes.data
            )
            
            health_info.save()

            logger.info(f"Aluno {new_student.full_name} cadastrado com sucesso.")
            
            return ApiResponse.success(message="Aluno cadastrado com sucesso!")

        except IntegrityError as e:
            db.session.rollback()
            logger.warning(f"Tentativa de duplicidade de CPF: {self.form.cpf.data}")
            return ApiResponse.error(message="Este CPF já está cadastrado no sistema.")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro inesperado ao criar aluno: {str(e)}")
            return ApiResponse.error(message="Ocorreu um erro interno no servidor.")

    def list_all(self):
        """Retorna todos os alunos ordenados por nome"""
        students = Student.query.order_by(Student.full_name).all()
        return ApiResponse.success(data=[s.to_dict() for s in students]) # Exemplo se tiver to_dict

    def delete_student(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return ApiResponse.error(message="Aluno não encontrado.")
            
        try:
            db.session.delete(student)
            db.session.commit()
            return ApiResponse.success(message="Aluno removido com sucesso!")
        except Exception as e:
            db.session.rollback()
            return ApiResponse.error(message="Não foi possível remover o aluno.")