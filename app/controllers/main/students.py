from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.controllers.forms.student_form import StudentForm
from app.services.student_service import StudentService
from . import main


@main.route('/students', methods=['GET', 'POST'])
@login_required
def page_students():
    form = StudentForm()
    service = StudentService(forms=form, request=request)

    if request.method == 'POST':
        return service.create_student()
    
    # Buscamos os alunos para a listagem inicial
    students = service.list_all(as_dict=False) # Certifique-se que o list_all() retorna a lista pura ou use Student.query...
    print(students)
    return render_template('page-students.html', form=form, students=students)