from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.views.auth import auth_views
import json

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
    tags = Tag.query.all()
    courses = Question.query.with_entities(Question.courseCode).distinct()
    questions = get_all_my_questions(current_user)
    return render_template('create_exam.html', tags=tags, courses=[c[0] for c in courses], questions=questions)

@exams_views.route('/filter_questions_exams', methods=['GET'])
def filter_questions_exams():
    difficulty = request.args.get('difficulty')
    tag = request.args.get('tag')
    course_code = request.args.get('course_code')

    query = Question.query

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if tag:
        query = query.join(Question.tag).filter(Tag.id == tag)
    if course_code:
        query = query.filter_by(courseCode=course_code)

    questions = query.all()
    return jsonify({
        'questions': [
            {
                'id': question.id,
                'text': question.text,
                'tag': [tag.tag_text for tag in question.tag],
                'difficulty': question.difficulty,
                'courseCode': question.courseCode,
            }
            for question in questions
        ]
    })

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
    question_ids = data.get('question_ids', [])  # Get the list of question IDs

    if not title:
        return jsonify({'message': 'Missing required data title'}), 400

    if not teacher_id:
        return jsonify({'message': 'Missing required data teacher_id'}), 400

    if not course_code:
        return jsonify({'message': 'Missing required data course_code'}), 400

    new_exam = Exam(
        teacher_id=teacher_id,
        title=title,
        course_code=course_code
    )

    # Associate the selected questions with the exam
    for question_id in question_ids:
        question = Question.query.get(question_id)
        if question:
            new_exam.exam_questions.append(question)

    db.session.add(new_exam)
    try:
        db.session.commit()
        return jsonify({'message': 'Exam created successfully', 'exam_id': new_exam.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating exam: {str(e)}'}), 500

@exams_views.route('/download_new_exam', methods=['POST'])
@login_required
def download_new_exam():
    user = current_user
    if not user.is_authenticated:
        return jsonify({'message': 'Unauthorized'}), 401

    # Get the last saved exam
    last_exam = Exam.query.filter_by(teacher_id=user.id).order_by(Exam.id.desc()).first()
    if not last_exam:
        return jsonify({'message': 'No exams found to download'}), 404

    # Use the last exam ID for downloading
    return download_exam(last_exam.id, format="pdf")

@exams_views.route('/download_exam/<int:exam_id>', methods=['GET'])
def download_exam_route(exam_id):
    return download_exam(exam_id, format="pdf")


@exams_views.route('/delete_exam/<int:exam_id>', methods=['DELETE'])
def delete_exam_route(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return jsonify({"error": "Exam not found"}), 404

    try:
        delete_exam(exam_id)  # Call the function to delete the exam
        return jsonify({"message": "Exam deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete exam: {str(e)}"}), 500

@exams_views.route('/edit_exam/<int:exam_id>', methods=['GET'])
@login_required
def edit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    questions = get_all_my_questions(current_user)

    # Get the IDs of the questions already in this exam
    exam_question_ids = [question.id for question in exam.exam_questions]
    exam_question_ids_json = json.dumps(exam_question_ids)  # Convert the list to a JSON string

    return render_template('editExams.html', exam=exam, questions=questions, exam_question_ids=exam_question_ids, exam_question_ids_json=exam_question_ids_json)

@exams_views.route('/edit_exam/<int:exam_id>', methods=['PUT'])
def edit_exam_route(exam_id):
    data = request.get_json()
    title = data.get('title')
    course_code = data.get('courseCode')
    add_questions = data.get('add_questions', [])
    remove_questions = data.get('remove_questions', [])
    teacher_id = data.get('teacher_id')  

    print("Remove Questions:", remove_questions)  

    result = update_exam(
        exam_id=exam_id,
        title=title,
        course_code=course_code,
        add_questions=add_questions,
        remove_questions=remove_questions
    )

    if "error" in result:
        return jsonify(result), 404
    return jsonify(result), 200






