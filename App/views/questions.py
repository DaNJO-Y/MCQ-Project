from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from.index import index_views

from App.controllers import *

questions_views = Blueprint('questions_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    
@questions_views.route('/questions', methods=['POST'])
def create_question():
    teacher = current_user
    teacher_id = teacher.id
    text = request.form.get('text')
    course_code = request.form.get('course-code')
    difficulty = request.form.get('difficulty') 
    options_data = request.form.get('options')
    question_image = request.files.get('questionImage')

    if not teacher_id or not difficulty or not course_code or not options_data:
        return jsonify({"error": "Missing required fields"}), 400

    if question_image:
      image_filename = save_image(question_image)
    image_filename = None

    options = []
    # import json
    for option_data in json.loads(options_data):
        body = option_data.get('body')
        image = option_data.get('image')
        is_correct = option_data.get('is_correct', False)
        # temp_image = 
        if image:
          image_filename = save_image(request.files.get(image.filename)) #get the file from the request files.
        image_filename=None
        option = Option(questionId=None, body=body, image=image_filename, is_correct=is_correct)
        options.append(option)

    question = Question(
        teacherId=teacher_id,
        text=text,
        difficulty=difficulty,
        courseCode=course_code,
        options=options
    )

    if image_filename:
        question.image = image_filename

    db.session.add(question)
    db.session.commit()

    for option in options:
        option.questionId = question.id
    db.session.commit()
    print(question.get_json())
    flash('Question Successfully created!')
    return jsonify(question.get_json()), 201



@questions_views.route('/myQuestions')
def my_questions_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login'))  # Redirect to login if not logged in

    user=current_user

    # questions = get_all_my_questions(user)  # Fetch only the logged-in teacher's questions
    print(user.id)
    questions = get_all_my_questions(user.id)
    # return render_template('MyQuestions.html', questions=questions)
    return render_template('MyQuestions.html')
