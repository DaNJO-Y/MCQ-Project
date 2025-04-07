from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.views.auth import auth_views

from.index import index_views

from App.controllers import *

exams_views = Blueprint('exams_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    

@exams_views.route('/myExams')
def my_exams_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login_action'))  # Redirect to login if not logged in

    response = get_exams(current_user, page=1, per_page=10)
    if isinstance(response, tuple):  # Handling error responses
        response, status = response
        if status == 404:
            flash("No exams found", "warning")
            response["exams"] = []

    return render_template('MyExams.html', exams=response["exams"])

@exams_views.route('/new_exam')

def newExamPage():
    questions = get_all_my_questions(current_user)
    return render_template('create_exam.html', questions=questions)

@exams_views.route('/save_exams', methods=['POST'])
@login_required
def save_the_exam():
    user = current_user

    if not user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    teacher_id = current_user.id
    title = data.get('title')
    course_code = data.get('courseCode')

    # if not all([teacher_id, title, course_code]):
    if not title:
        return jsonify({'message': 'Missing required data title'}), 400
   
    if not teacher_id:
        return jsonify({'message': 'Missing required data teacher_id'}), 400
        # return jsonify({'message': 'Missing required data $title, $course_code'}), 400
    if not course_code:
        return jsonify({'message': 'Missing required data course_code'}), 400

    new_exam = Exam(
        teacher_id=teacher_id,
        title=title,
        course_code=course_code
    )

    db.session.add(new_exam)
    try:
        db.session.commit()
        return jsonify({'message': 'Exam created successfully', 'exam_id': new_exam.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating exam: {str(e)}'}), 500
    

@exams_views.route('/download_my_exams', methods=['POST'])
@login_required
def download_my_exams():
    user = current_user
    if not user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    # Get the last saved exam
    last_exam = Exam.query.filter_by(teacher_id=user.id).order_by(Exam.id.desc()).first()
    if not last_exam:
        return jsonify({'message': 'No exams found to download'}), 404

    # Use the last exam ID for downloading
    return download_exam(last_exam.id, format="pdf")