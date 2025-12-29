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

    
    def _ajuste_weigth(self,weight=None):
        if 'kg'.lower() in weight:
            return float(str(weight).replace('kg'.lower(),'').replace(',','.'))
        return float(weight)
    
    def _ajuste_weigth(self,weight=None):
        if 'kg'.lower() in weight:
            return float(str(weight).replace('kg'.lower(),'').replace(',','.'))
        return float(weight)
    
    def clean_mask(self,value):
        return "".join(filter(str.isdigit, value)) if value else None


    def create_student(self):
        """Lógica de negócio para criação de aluno com retorno padronizado"""
        
        # 1. Validação do formulário
        if not self.form or not self.form.validate_on_submit():
            # Se o form for inválido, extraímos os erros para o SweetAlert mostrar
            
            errors = {field: err[0] for field, err in self.form.errors.items()}
            print(errors)
            return ApiResponse.error(message="Erro de validação", errors=errors)

        try:
            student_id = self.form.student_id.data # Adicione esse campo no seu StudentForm
    
            if student_id:
                # LÓGICA DE ATUALIZAÇÃO
                # --- LÓGICA DE ATUALIZAÇÃO (EDITAR) ---
                    student = Student.query.get(student_id)
                    if not student:
                        return ApiResponse.error(message="Aluno não encontrado para edição.")

                    # Atualiza Dados Pessoais e Endereço
                    student.full_name = self.form.full_name.data
                    student.cpf = self.clean_mask(self.form.cpf.data)
                    student.email = self.form.email.data
                    student.phone = self.clean_mask(self.form.phone.data)
                    student.birth_date = self.form.birth_date.data
                    student.postal_code = self.form.postal_code.data
                    student.address = self.form.address.data
                    student.address_number = self.form.address_number.data
                    student.city = self.form.city.data
                    student.emergency_contact = self.form.emergency_contact.data
                    student.emergency_phone = self.clean_mask(self.form.emergency_phone.data)

                    # Atualiza Dados de Saúde (Tabela Relacionada)
                    health = StudentHealth.query.filter_by(student_id=student.id).first()
                    if not health:
                        # Caso por algum erro o aluno não tenha registro de saúde, criamos um
                        health = StudentHealth(student_id=student.id)
                        db.session.add(health)

                    health.blood_type = self.form.blood_type.data
                    health.weight = self.form.weight.data
                    health.height = self.form.height.data
                    health.medical_notes = self.form.medical_notes.data

                    db.session.commit()
                    return ApiResponse.success(message="Cadastro do aluno atualizado com sucesso!")
            else:
                # 2. Instância do Aluno
                # 1. Instância do Aluno (Dados Principais, Endereço e Contato)
                new_student = Student(
                    full_name=self.form.full_name.data,
                    cpf=self.clean_mask(self.form.cpf.data), # LIMPA AQUI
        
                    email=self.form.email.data,
                    phone=self.clean_mask(self.form.phone.data),
                    birth_date=self.form.birth_date.data,
                    # Endereço
                    postal_code=self.form.postal_code.data,
                    address=self.form.address.data,
                    address_number=self.form.address_number.data,
                    city=self.form.city.data,
                    # Emergência
                    emergency_contact=self.clean_mask(self.form.emergency_contact.data),
                    emergency_phone=self.form.emergency_phone.data
                )
                db.session.add(new_student)
                db.session.flush()

                # 2. Instância dos Dados de Saúde (Tabela Separada)
                health_info = StudentHealth(
                    student_id=new_student.id,
                    blood_type=self.form.blood_type.data,
                    weight=self.form.weight.data,
                    height=self.form.height.data, # Adicionado altura
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

    def list_all(self, as_dict=False):
        """Retorna todos os alunos. Se as_dict for True, retorna para JSON."""
        students = Student.query.order_by(Student.full_name).all()
        
        if as_dict:
            return [s.to_dict() for s in students]
        
        return students # Retorna a lista de objetos para o Jinj # Exemplo se tiver to_dict

    def delete_student(self, student_id):
        try:
            student = Student.query.get(student_id)
            if not student:
                return ApiResponse.error(message="Aluno não encontrado.")

            # 1. Remove os registros de saúde
            StudentHealth.query.filter_by(student_id=student_id).delete()
            
            # 2. Remove as matrículas vinculadas (Isso resolve o erro da NotNullViolation)
            # Importe o modelo Enrollment se necessário
            from app.models.pages.academy import Enrollment 
            Enrollment.query.filter_by(student_id=student_id).delete()
            
            # 3. Agora exclui o aluno
            db.session.delete(student)
            db.session.commit()
            
            return ApiResponse.success(message="Aluno e matrículas excluídos com sucesso.")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao excluir aluno: {str(e)}")
            return ApiResponse.error(message="Erro: Este aluno possui vínculos que não puderam ser removidos.")
            

    def get_student_details(self, student_id=None):
        from app.models.pages.students import Student
        from app.models.pages.academy import Enrollment
        try:
            student = Student.query.get(student_id)
            if not student:
                return ApiResponse.error(message="Aluno não encontrado.")
            
            student_health = StudentHealth.get_student_id(student.id)

            # BUSCAR MATRÍCULAS USANDO LIST COMPREHENSION
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()

            enrollment_data = [
                {
                    # Aqui usamos 'activity_ref' que é o backref vindo de Activity
                    "class_name": en.schedule.activity_ref.name if en.schedule and en.schedule.activity_ref else "Atividade não definida",
                    "status": en.status,
                    "start_date": en.enrollment_date.strftime('%d/%m/%Y') if en.enrollment_date else "---"
                } 
                for en in enrollments
            ]

            # Montamos um dicionário com todos os dados para o modal
            student_data = {
                    "full_name": student.full_name,
                    "cpf": student.cpf or "",
                    "email": student.email or "",
                    "phone": student.phone or "",
                    "birth_date": student.birth_date.strftime('%d/%m/%Y') if student.birth_date else "",
                    "birth_date_iso": student.birth_date.strftime('%Y-%m-%d') if student.birth_date else "",
                    "is_active": student.is_active,
                    "blood_type": student_health.blood_type or "",
                    "weight": f"{student_health.weight}" if student_health.weight else "",
                    "height": f"{student_health.height}" if student_health.height else "",
                    "medical_notes": student_health.medical_notes or "Nenhuma observação.",
                    "emergency_contact": student.emergency_contact or "",
                    "emergency_phone": student.emergency_phone or "",
                    "postal_code": student.postal_code or "",
                    "address": student.address or "",
                    "address_number": student.address_number or "",
                    "city": student.city or "",
                    "enrollments":enrollment_data
                }
            return ApiResponse.success(data=student_data)
        except Exception as e:
            return ApiResponse.error(message=str(e))
        
    def toggle_student_status(self, student_id=None):
        from app.models.pages.students import Student
        from app import db # <--- Verifique se este caminho está correto conforme seu projeto
        
        try:
            student = Student.query.get(student_id)
            if not student:
                return ApiResponse.error(message="Aluno não encontrado.")
            
            # Faz a troca
            student.is_active = not student.is_active
            db.session.commit()
            
            msg = "ativado" if student.is_active else "inativado"
            return ApiResponse.success(message=f"Aluno {msg} com sucesso!")
        except Exception as e:
            db.session.rollback()
            # Isso vai imprimir o erro real no seu terminal do VS Code/Linux
            print(f"ERRO NO BANCO: {str(e)}") 
            return ApiResponse.error(message="Falha ao atualizar banco de dados.")
        
    