from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.views.auth import auth_views
from docx import Document
import io
from App.database import db
from App.models import Question, Option, Tag 


from App.controllers import *

import_page_views = Blueprint('import_page_views', __name__, template_folder='../templates')

'''
Page/Action Routes
''' 

@import_page_views.route('/import')
def import_page():
    return render_template('import_questions.html')

questions_data = []

def extract_questions_from_text(text):
    questions = []
    current_question = {}
    options_started = False
    option_counter = 'A'

    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # print(f"Processing line: '{line}'")

        if line.startswith("CourseCode:"):
            current_question['courseCode'] = line.split(":")[1].strip()
        elif line.startswith("Difficulty:"):
            current_question['difficulty'] = line.split(":")[1].strip().upper()
        elif line.startswith("Question:"):
            if current_question.get('text'):
                questions.append(current_question)
            current_question = {'options': {}}
            current_question['text'] = line.split(":")[1].strip()
            options_started = True
            option_counter = 'A'
        elif line.startswith("Tags:"):
            current_question['tags'] = [tag.strip() for tag in line.split(":")[1].strip().split(',')]
        elif options_started:
            if line.startswith(f"{option_counter}:"):
                current_question['options'][option_counter] = line.split(":")[1].strip()
                option_counter = chr(ord(option_counter) + 1)
            elif line.startswith("Correct:"):
                current_question['correct_answer'] = line.split(":")[1].strip().upper()
                options_started = False

    if current_question.get('text'):
        questions.append(current_question)

    return questions

@import_page_views.route('/upload_text_tags', methods=['GET', 'POST'])
def upload_text_tags():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            file_extension = file.filename.rsplit('.', 1)[1].lower()

            if file_extension == 'txt':
                file_content = file.read().decode('utf-8')
            elif file_extension == 'docx':
                try:
                    doc = Document(io.BytesIO(file.read()))
                    file_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except Exception as e:
                    flash(f"Error reading DOCX file: {e}", 'error')
                    return redirect(request.url)
            else:
                flash("Invalid file format. Only .txt and .docx files are supported.", 'error')
                return redirect(request.url)

            global questions_data
            questions_data = extract_questions_from_text(file_content)
            if questions_data:
                return redirect(url_for('import_page_views.create_questions_with_tags'))
            else:
                flash("No questions found in the uploaded file.", 'info')
                return redirect(request.url)
        else:
            flash("No file selected.", 'warning')
            return redirect(request.url)
    return render_template('upload_text.html')

@import_page_views.route('/create_questions_with_tags')
@login_required
def create_questions_with_tags():
    global questions_data
    if not questions_data:
        return "No question data available to create."

    # teacher_id = 1 # Replace with the actual logged-in teacher's ID
    user = current_user
    for q_data in questions_data:
        question = Question(
            teacherId=user.id,
            text=q_data['text'],
            difficulty=q_data.get('difficulty'),
            courseCode=q_data.get('courseCode'),
            options=[]
        )

        # Add tags
        if 'tags' in q_data:
            for tag_name in q_data['tags']:
                tag = Tag.query.filter_by(tag_text=tag_name).first()
                if not tag:
                    tag = Tag(question_id=question.id, tag_text=tag_name)
                    db.session.add(tag)
                question.tag.append(tag)

        db.session.add(question)
        db.session.commit()

        for option_key, option_text in q_data['options'].items():
            is_correct = (option_key == q_data.get('correct_answer'))
            option = Option(
                questionId=question.id,
                body=option_text,
                image=None,
                is_correct=is_correct
            )
            db.session.add(option)

    db.session.commit()
    
    questions_data = []
    return "Questions and tags created successfully!"

# @import_page_views.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     questions_from_db = Question.query.all()
#     if not questions_from_db:
#         return "No questions available."

#     if request.method == 'POST':
#         score = 0
#         for i, question in enumerate(questions_from_db):
#             user_answer_id = request.form.get(f'question_{question.id}')
#             correct_option = next((opt for opt in question.options if opt.is_correct), None)
#             if correct_option and str(correct_option.id) == user_answer_id:
#                 score += 1
#         return render_template('results.html', score=score, total=len(questions_from_db))

#     return render_template('quiz.html', questions=questions_from_db)

