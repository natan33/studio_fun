from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from app.controllers.forms.student_form import StudentForm
from app.services.student_service import StudentService
from . import main


@main.route('/students', methods=['GET', 'POST'])
@login_required
def page_students():
    form = StudentForm()
    service = StudentService(form)
    
    if service.create_student():
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('students.index'))
    
    return render_template('students.html', form=form)