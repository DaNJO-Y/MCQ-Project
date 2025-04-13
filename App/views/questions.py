from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for, current_app
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
# app = Flask(__name__)  # Replace with your actual app initialization
# app.config['UPLOAD_FOLDER'] = 'UPLOADS'  # Set your upload folder
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_image(file):
    if file:
        try:
            filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            # print(f"Attempting to save to: {file_path}")
            file.save(file_path)
            # print(f"Image saved successfully as: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    return None

def delete_image_from_storage(filename):
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted image: {filepath}")
    except Exception as e:
        print(f"Error deleting image {filepath}: {e}")

'''
Page/Action Routes
'''    

@questions_views.route('/myQuestions')
def my_questions_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login_action'))  # Redirect to login if not logged in

    tags= Tag.query.all()  # Fetch all tags
    
    questions = get_all_my_questions(current_user)  # Fetch only the logged-in teacher's questions
    courses = [question.courseCode for question in questions]
    # Remove duplicates while preserving order
    seen = set()
    courses = [x for x in courses if not (x in seen or seen.add(x))]
    
    
    return render_template('MyQuestions.html', tags=tags,courses=courses, questions=questions)

@questions_views.route('/displayQuestion/<int:question_id>',methods=['GET'])
@login_required
def displayQuestionPage(question_id):
    question = get_question(question_id)
    if not question:
        flash('Question not found')
        return jsonify({"error": "No question data"}), 400
    user = current_user
    teacher = get_teacher(user.id)
    if not teacher:
        flash('Teacher is not logged in.')
        return jsonify({"error": "Not teacher data"}), 400
    chosenQuestion = ""
    for q in teacher.questions:
        if q.id == question.id:
            chosenQuestion = q
    print(chosenQuestion.get_json()) 
    exam_id_list = get_questions_exams(question_id)
    exams = getExam(teacher.my_exams, exam_id_list)
    return render_template('display_question.html', question=chosenQuestion, exams=exams)

def getExam(teacher_exams, potential_exam_ids):
    exam_list = []
    for exam in teacher_exams:
        if exam.id in potential_exam_ids:
            exam_list.append(exam)
    return exam_list

@questions_views.route('/filter_questions', methods=['GET'])
def filter_questions():
    difficulty = request.args.get('difficulty')  # Get the selected difficulty
    tag_id = request.args.get('tag')  # Get the selected tag ID
    course_code = request.args.get('course_code')  # Get the selected course code

    filtered_questions=filter(difficulty, tag_id, course_code)
    # Pass the filtered questions, tags, and course codes back to the template
    tags = Tag.query.all()
    courses = Question.query.with_entities(Question.courseCode).distinct()  # Get unique course codes
    return render_template('MyQuestions.html', questions=filtered_questions, tags=tags, courses=[c[0] for c in courses])

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
    print(f"Received question_image: {question_image}")

    if not teacher_id or not difficulty or not course_code or not options_data:
        return jsonify({"error": "Missing required fields"}), 400

    question_image_filename = None
    if question_image:
        question_image_filename = save_image(question_image)
        # print(f"Saved filename: {question_image_filename}")

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
        
        option = create_option(question_id=None, body=body, image=image_filename, is_correct=is_correct)
        options.append(option)

    question = save_question(
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

    for option in question.options:
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

@questions_views.route('/editQuestionPage/<int:question_id>',methods=['GET'])
@login_required
def editQuestionsPage(question_id):
    question = get_question(question_id)
    if not question:
        flash('Question not found')
        return jsonify({"error": "No question data"}), 400
    user = current_user
    teacher = get_teacher(user.id)
    if not teacher:
        flash('Teacher is not logged in.')
        return jsonify({"error": "Not teacher data"}), 400
    chosenQuestion = ""
    for q in teacher.questions:
        if q.id == question.id:
            chosenQuestion = q
    print(chosenQuestion.get_json()) 
    return render_template('editQuestion.html', question=chosenQuestion)



@questions_views.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    potentialQuestion = get_question(question_id)
    if not potentialQuestion:
        flash('Question not found')
        return jsonify({"error": "No question data"}), 400
    user = current_user
    teacher = get_teacher(user.id)
    if not teacher:
        flash('Teacher is not logged in.')
        return jsonify({"error": "Not teacher data"}), 400
    question = ""
    for q in teacher.questions:
        if q.id == potentialQuestion.id:
            question = q

    if request.method == 'GET':
        return render_template('editQuestion.html', question=question)
    
    elif request.method == 'POST':
        try:
            # Process main question data
            question.text = request.form.get('text')
            question.courseCode = request.form.get('course-code')
            question.difficulty = request.form.get('difficulty')

            # Handle image removal
            if request.form.get('remove_image'):
                if question.image:
                    delete_image_from_storage(question.image)
                    question.image = None

            # Handle new image upload
            new_question_image = request.files.get('question_image')
            if new_question_image and new_question_image.filename != '':
                if question.image:
                    delete_image_from_storage(question.image)
                filename = save_image(new_question_image)
                if filename:
                    question.image = filename

            correct_option_value = request.form.get('correct_option')

            # Process existing options
            existing_options = {}
            for key, value in request.form.items():
                if key.startswith('option_id_'):
                    option_index = key.split('_')[-1]
                    existing_options[option_index] = int(value)

            # Update existing options
            for index, option_id in existing_options.items():
                option = Option.query.get(option_id)
                if option:
                    # Update option body
                    body_key = f'option_body_{index}'
                    if body_key in request.form:
                        option.body = request.form[body_key]
                    
                    # Update correct status
                    # correct_key = f'optionCorrect_{index}'
                    # option.is_correct = correct_key in request.form
                    option.is_correct = (str(option.id) == correct_option_value)
                    
                    # Handle image removal
                    remove_key = f'remove_option_image_{index}'
                    if remove_key in request.form and option.image:
                        delete_image_from_storage(option.image)
                        option.image = None
                    
                    # Handle image upload
                    image_key = f'option_image_{index}'
                    if image_key in request.files:
                        image_file = request.files[image_key]
                        if image_file and image_file.filename != '':
                            if option.image:
                                delete_image_from_storage(option.image)
                            filename = save_image(image_file)
                            if filename:
                                option.image = filename

            # Process new options
            new_options = {}
            for key in request.form:
                if key.startswith('option_body_new_'):
                    temp_id = key.split('_')[-1]
                    new_options[temp_id] = {
                        'body': request.form[key],
                        # 'is_correct': f'optionCorrect_new_{temp_id}' in request.form,
                        'is_correct': f'new_{temp_id}' == correct_option_value,
                        'image': None
                    }

            # Handle images for new options
            for key, file in request.files.items():
                if key.startswith('option_image_new_'):
                    temp_id = key.split('_')[-1]
                    if temp_id in new_options and file.filename != '':
                        filename = save_image(file)
                        if filename:
                            new_options[temp_id]['image'] = filename

            # Create new options
            for temp_id, option_data in new_options.items():
                new_option = create_option(question_id=question.id, body=option_data['body'], image=option_data['image'], is_correct=option_data['is_correct'])
                db.session.add(new_option)

            # Handle deleted options
            for key, value in request.form.items():
                if key.startswith('delete_option_') and value == 'true':
                    option_id = int(key.split('_')[-1])
                    option = Option.query.get(option_id)
                    if option:
                        if option.image:
                            delete_image_from_storage(option.image)
                        db.session.delete(option)

            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('tags_views.editTagsPage', question_id=question_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'error')
            current_app.logger.error(f"Error updating question: {str(e)}")
            return redirect(url_for('questions_views.edit_question', question_id=question_id))

@questions_views.route('/api/create_question', methods=['POST'])
@login_required
def user_api_create_questions():
    try: 
        teacher = current_user
        data = request.json
        if not data or 'text' not in data or 'difficulty' not in data or 'courseCode' not in data:
            return jsonify({"error":"Required fields missing"}), 400
        
        # options_list=[]
        question = save_question(teacherId=teacher.id, text=data['text'], difficulty=data['difficulty'], courseCode=data['courseCode'],options=[])
        if not question:
            return jsonify({"error":"Question data was not formatted properly"}), 400
        option_1 = create_option(question_id=question.id, body=data['option_1_text'], image=None,is_correct=False)
        # options_list.append(option_1)
        option_2 = create_option(question_id=question.id, body=data['option_2_text'], image=None,is_correct=False)
        # options_list.append(option_2)
        option_3 = create_option(question_id=question.id, body=data['option_3_text'], image=None,is_correct=False)
        # options_list.append(option_3)
        option_4 = create_option(question_id=question.id, body=data['option_4_text'], image=None,is_correct=True)
        # options_list.append(option_4)

        if associate_option(question.id, option_1) and associate_option(question.id, option_2) and associate_option(question.id, option_3) and associate_option(question.id, option_4):
            return jsonify({"message": "Question created and options associated successfully"}), 200
    except Exception as e:
        return jsonify(error="An Error Occurred While Creating the question"), 500

def help_populate_questions(teacher_id, focus):
    teacher = get_teacher(teacher_id)
    if teacher:
        if focus == "courseCode":
            question_1 = save_question(teacherId=teacher_id, text="Test question for course code", difficulty="Easy", courseCode="TestCourse 101",options=[])
            
            option_1 = create_option(question_id=question_1.id, body="Test option CC 1", image=None,is_correct=False)
            option_2 = create_option(question_id=question_1.id, body="Test option CC 2", image=None,is_correct=False)
            option_3 = create_option(question_id=question_1.id, body="Test option CC 3", image=None,is_correct=False)
            option_4 = create_option(question_id=question_1.id, body="Test option CC 4", image=None,is_correct=True)
            associate_option(question_1.id, option_1)
            associate_option(question_1.id, option_2)
            associate_option(question_1.id, option_3)
            associate_option(question_1.id, option_4)

            teacher.questions.append(question_1)

            question_2 = save_question(teacherId=teacher_id, text="Test question for course code number 2", difficulty="Hard", courseCode="TestCourse 101",options=[])
            
            option_a = create_option(question_id=question_2.id, body="Test option CC 1", image=None,is_correct=False)
            option_b = create_option(question_id=question_2.id, body="Test option CC 2", image=None,is_correct=False)
            option_c = create_option(question_id=question_2.id, body="Test option CC 3", image=None,is_correct=False)
            option_d = create_option(question_id=question_2.id, body="Test option CC 4", image=None,is_correct=True)
            associate_option(question_2.id, option_a)
            associate_option(question_2.id, option_b)
            associate_option(question_2.id, option_c)
            associate_option(question_2.id, option_d)

            teacher.questions.append(question_2)

        
        if focus == "difficulty":
            question_1 = save_question(teacherId=teacher_id, text="Test question for difficulty", difficulty="Easy", courseCode="TestCourse 101",options=[])
            
            option_1 = create_option(question_id=question_1.id, body="Test option CC 1", image=None,is_correct=False)
            option_2 = create_option(question_id=question_1.id, body="Test option CC 2", image=None,is_correct=False)
            option_3 = create_option(question_id=question_1.id, body="Test option CC 3", image=None,is_correct=False)
            option_4 = create_option(question_id=question_1.id, body="Test option CC 4", image=None,is_correct=True)
            associate_option(question_1.id, option_1)
            associate_option(question_1.id, option_2)
            associate_option(question_1.id, option_3)
            associate_option(question_1.id, option_4)

            teacher.questions.append(question_1)

            question_2 = save_question(teacherId=teacher_id, text="Test question for difficulty 2", difficulty="Intermediate", courseCode="TestCourse 101",options=[])
            
            option_a = create_option(question_id=question_2.id, body="Test option CC 1", image=None,is_correct=False)
            option_b = create_option(question_id=question_2.id, body="Test option CC 2", image=None,is_correct=False)
            option_c = create_option(question_id=question_2.id, body="Test option CC 3", image=None,is_correct=False)
            option_d = create_option(question_id=question_2.id, body="Test option CC 4", image=None,is_correct=True)
            associate_option(question_2.id, option_a)
            associate_option(question_2.id, option_b)
            associate_option(question_2.id, option_c)
            associate_option(question_2.id, option_d)

            teacher.questions.append(question_2)

            question_3 = save_question(teacherId=teacher_id, text="Test question for ", difficulty="Hard", courseCode="TestCourse 101",options=[])
            
            option_e = create_option(question_id=question_3.id, body="Test option CC 1", image=None,is_correct=False)
            option_f = create_option(question_id=question_3.id, body="Test option CC 2", image=None,is_correct=False)
            option_g = create_option(question_id=question_3.id, body="Test option CC 3", image=None,is_correct=False)
            option_h = create_option(question_id=question_3.id, body="Test option CC 4", image=None,is_correct=True)
            associate_option(question_3.id, option_e)
            associate_option(question_3.id, option_f)
            associate_option(question_3.id, option_g)
            associate_option(question_3.id, option_h)

            teacher.questions.append(question_3)

        db.session.add(teacher)
        db.session.commit()
        return True
    return False
    
@questions_views.route('/api/get_teacher_question', methods=['GET'])
@login_required
def user_api_get_questions():
    try:
        teacher = current_user
        if not teacher:
            return jsonify({"error":"Unauthourized user"}), 400
        questions_list = [question.get_json() for question in teacher.questions]
        # print(questions_list)
        return jsonify(questions_list), 200
    except Exception as e:
        return jsonify(error="An Error Occurred While retrieving the questions"), 500


@questions_views.route('/api/get_question_by_courseCode/<string:coursecode>', methods=['GET'])
@login_required
def user_api_get_questions_by_courseCode(coursecode):
    # print(coursecode)
    try:
        teacher = current_user
        if not teacher:
            return jsonify({"error":"Unauthourized user"}), 400
        # help_populate_questions(teacher.id, "courseCode")
        list = get_questions_by_course_code(teacher.id, coursecode)
        question_list = [q.get_json() for q in list]
        # print(question_list)
        return jsonify(question_list), 200
    except Exception as e:
        return jsonify(error=f"An Error Occurred While retrieving the questions by course code: {coursecode}"), 500
        
@questions_views.route('/api/get_question_by_difficulty/<string:difficulty>', methods=['GET'])
@login_required
def user_api_get_questions_by_difficulty(difficulty):
    try:
        teacher = current_user
        if not teacher:
            return jsonify({"error":"Unauthourized user"}), 400
        if help_populate_questions(teacher.id, "difficulty"):
            list = get_questions_by_difficulty(teacher.id, difficulty)
            question_list = [q.get_json() for q in list]
            # print(question_list)
            return jsonify(question_list), 200
    except Exception as e:
        return jsonify(error=f"An Error Occurred While retrieving the questions by course code: {coursecode}"), 500

# @questions_views.route('/api/update_question', methods=['POST'])
# @questions_views.route('/api/delete_question', methods=['DELETE'])


        
        