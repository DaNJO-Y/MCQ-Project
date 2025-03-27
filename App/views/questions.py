from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from.index import index_views
from App.models import *

from App.controllers import *
import os
import uuid
import json
from.index import index_views
from .auth import auth_views

questions_views = Blueprint('questions_views', __name__, template_folder='../templates')
app = Flask(__name__)  # Replace with your actual app initialization
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set your upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_image(file):
    if file:
        try:
            filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

'''
Page/Action Routes
'''    

@questions_views.route('/myQuestions')
def my_questions_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login'))  # Redirect to login if not logged in

    questions = get_all_my_questions(current_user)  # Fetch only the logged-in teacher's questions
    return render_template('MyQuestions.html', questions=questions)

@questions_views.route('/displayQuestion',methods=['GET'])
def displayQuestionPage():
    return render_template('display_question.html')

@questions_views.route('/createQuestion',methods=['GET'])
def createQuestionPage():
    return render_template('create_question.html')

@questions_views.route('/questions', methods=['POST'])
@login_required
def create_question():
    teacher = current_user
    teacher_id = teacher.id
    text = request.form.get('text')
    course_code = request.form.get('course-code')
    difficulty = request.form.get('difficulty') 
    options_data = request.form.get('options')
    # question_image = request.files.get('questionImage')
    question_image = request.files.get('questionImage')
    

    if not teacher_id or not difficulty or not course_code or not options_data:
        return jsonify({"error": "Missing required fields"}), 400

    question_image_filename = None
    if question_image:
        question_image_filename = save_image(question_image)

    try:
        options_d = json.loads(options_data)  # Parse the JSON string
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format for options"}), 400

    options = []
    for option_data in options_d:
        body = option_data.get('body')
        image_input_name = option_data.get('image')  # Get the string name
        image_filename = None
        if image_input_name:
            image_file = request.files.get(image_input_name)
            if image_file:
                image_filename = save_image(image_file)
        is_correct = option_data.get('is_correct', False)
        
        option = Option(questionId=None, body=body, image=image_filename, is_correct=is_correct)
        options.append(option)

    question = Question(
        teacherId=teacher_id,
        text=text,
        difficulty=difficulty,
        courseCode=course_code,
        options=options
    )

    if question_image_filename:
        question.image = question_image_filename

    db.session.add(question)
    db.session.commit()

    for option in options:
        option.questionId = question.id
    db.session.commit()
    user = current_user
    if teacher_id == user.id:
        teacher = get_teacher(teacher_id)
        # print(teacher)
        teacher.questions.append(question)
        db.session.commit()

    print(question.get_json())
    # print(teacher.questions)
    flash('Question Successfully created!')
    return jsonify(question.get_json()), 201

@questions_views.route('/delete/<int:question_id>', methods=['GET'])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.teacherId == current_user.id:  # Ensure the user owns the question
        try:
            # Delete associated options first (if necessary, depending on your database setup)
            for option in question.options:
                db.session.delete(option)
            db.session.delete(question)
            db.session.commit()
            flash('Question deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting question: {e}', 'error')
    else:
        flash('You do not have permission to delete this question.', 'warning')
    return redirect(url_for('questions_views.my_questions_page'))