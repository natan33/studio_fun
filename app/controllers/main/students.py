from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.models.pages.finance import Plan
from app.controllers.forms.student_form import StudentForm
from app.services.student_service import StudentService
from . import main


@main.route('/students', methods=['GET', 'POST'])
@login_required
def page_students():
    form = StudentForm()
    service = StudentService(forms=form, request=request)

    plans = Plan.query.all()
    # Opção A: Usando listas (Mais recomendado)
    form.plan_id.choices = [(0, 'Selecione um plano')] + [(p.id, f"{p.name} (R$ {p.price})") for p in plans]
    
    if request.method == 'POST':
        return service.create_student()
    
    # Buscamos os alunos para a listagem inicial
 # Certifique-se que o list_all() retorna a lista pura ou use Student.query...
    return render_template('page-students.html', form=form)