from flask import Blueprint, jsonify
from app.services.student_service import StudentService
from . import api
from flask_login import login_required

@api.route('/api/student/<int:id>', methods=['GET'])
@login_required
def get_student(id):
    service = StudentService()
    return  service.get_student_details(id)

@api.route('/api/student/toggle-status/<int:id>', methods=['POST'])
@login_required
def toggle_status(id):
    service = StudentService()
    return service.toggle_student_status(id)

@api.route('/api/student/delete/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    service = StudentService()
    return service.delete_student(student_id)