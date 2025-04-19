from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.controllers.question import associate_option, get_all_my_questions, save_question
from App.controllers.teacher import myExams
from App.views.auth import auth_views
from datetime import date
import json
from collections import Counter
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
@login_required
def newExamPage():
    teacher = current_user
    tags= Tag.query.all()  # Fetch all tags
    
    questions = get_all_my_questions(current_user)  # Fetch only the logged-in teacher's questions
    courses = [question.courseCode for question in questions]
    difficulties = [question.difficulty for question in questions]
    # Remove duplicates while preserving order
    seen = set()
    courses = [x for x in courses if not (x in seen or seen.add(x))]
    difficulties = [x for x in difficulties if not (x in seen or seen.add(x))]
    return render_template('create_exam.html', tags=tags, courses=courses, questions=questions, difficulties=difficulties)

@exams_views.route('/filter_questions_exams', methods=['GET'])
def filter_questions_exams():
    difficulty = request.args.get('difficulty')
    tag = request.args.get('tag')
    course_code = request.args.get('course_code')

    query = Question.query

    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if tag:
        # Ensure tag is queried by name or ID as needed
        query = query.filter(Question.tag).filter(Tag.id == tag)
    if course_code:
        # Ensure the filter is applied to the Question model
        query = query.filter(Question.courseCode == course_code)

    questions = query.all()
    return jsonify({
        'questions': [
            {
                'id': question.id,
                'text': question.text,
                'tag': [tag.tag_text for tag in question.tag],
                'difficulty': question.difficulty,
                'courseCode': question.courseCode,
                'options': [option.body for option in question.options],
                'option_isCorrect': [option.body for option in question.options if option.is_correct],
                'lastUsed': question.lastUsed,
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
            question.lastUsed = date.today()
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
    questions = Question.query.filter_by(teacherId=current_user.id).all()#all questions of the current user
    exam_question_ids_json = json.dumps(exam_question_ids)  # Convert the list to a JSON string
    tags = Tag.query.all()
    # courses = [course[0] for course in Question.query.with_entities(Question.courseCode).distinct()]
    courses = [question.courseCode for question in questions]
    difficulties = [question.difficulty for question in questions]
    # Remove duplicates while preserving order
    seen = set()
    courses = [x for x in courses if not (x in seen or seen.add(x))]
    difficulties = [x for x in difficulties if not (x in seen or seen.add(x))]
    return render_template('editExams.html', exam=exam, questions=questions, exam_question_ids=exam_question_ids, exam_question_ids_json=exam_question_ids_json,tags=tags,courses=courses, difficulties=difficulties)

@exams_views.route('/edit_exam/<int:exam_id>', methods=['PUT'])
def edit_exam_route(exam_id):
    data = request.get_json()
    print("Received Data:", data)  # Log the received data

    title = data.get('title')
    course_code = data.get('courseCode')
    add_questions = data.get('add_questions', [])
    remove_questions = data.get('remove_questions', [])
    teacher_id = data.get('teacher_id')  

    print("Add Questions:", add_questions)  # Log the questions to be added
    print("Remove Questions:", remove_questions)  # Log the questions to be removed

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

@exams_views.route('/api/create_exam', methods=['POST'])
@login_required
def user_api_create_exam():
    try:
        teacher = current_user
        data = request.json
        if not data or 'title' not in data or 'course_code' not in data:
            return jsonify({'error':'Missing required data'}), 400
        # title = data['title']
        # course_code = data['course_code']
        # text_1 = data['text_1']
        # text_2 = data['text_2']
        # difficulty_1 = data['difficulty_1']
        # difficulty_2 = data['difficulty_2']
        # body_1 = data['option_1']
        # body_2 = data['option_2']
        # body_3 = data['option_3']
        # body_4 = data['option_4']
        question_1 =  save_question(teacherId=teacher.id, text=data['text_1'], difficulty=data['difficulty_1'], courseCode=data['course_code'], options=[])
        if not question_1:
            return jsonify({'error':'Failed to save question 1'}), 400
        option_1 = create_option(question_id=question_1.id, body=data['option_1'], image=None, is_correct=False)
        option_2 = create_option(question_id=question_1.id, body=data['option_2'], image=None, is_correct=False)
        option_3 = create_option(question_id=question_1.id, body=data['option_3'], image=None, is_correct=True)
        option_4 = create_option(question_id=question_1.id, body=data['option_4'], image=None, is_correct=False)
        if not option_1 or not option_2 or not option_3 or not option_4:
            return jsonify({'error':'Failed to save options'}), 400
        associate_option(question_1.id, option_1) 
        associate_option(question_1.id, option_2) 
        associate_option(question_1.id, option_3) 
        associate_option(question_1.id, option_4)
        question_2 = save_question(teacherId=teacher.id, text=data['text_2'], difficulty=data['difficulty_2'], courseCode=data['course_code'], options=[])
        if not question_2:
            return jsonify({'error':'Failed to save question 2'}), 400
        questions_id = [question_1.id, question_2.id]
        exam_json = create_exam(title=data['title'], course_code=data['course_code'], questions=[], teacher_id=teacher.id)
        if add_questions(id=exam_json['id'], question_ids=questions_id) == True:
            return jsonify ({'message':'Exam created successfully'}), 200
    except Exception as e:
        # return jsonify(error="Failed to create exam"),500
        return jsonify(error=f"Failed to create exam: {str(e)}"), 500
    
@exams_views.route('/api/update_exam_details/<int:exam_id>', methods=['PUT'])
@login_required
def user_api_update_exam_details(exam_id):
    try:
        teacher = current_user
        data = request.json
        if not data or 'title' not in data or 'course_code' not in data:
            return jsonify({'error':'Missing required data'}), 400
        if not teacher:
            return jsonify({'error':'Unauthorized'}), 401
        exam_id_list = [e.id for e in teacher.my_exams]
        if exam_id not in exam_id_list:
            return jsonify({'error':'Invalid Id'}), 401
        
        exam = get_exam_and_return_exam(exam_id)
      
        response = update_exam(exam_id=exam_id, title=data['title'], course_code=data['course_code'], add_questions=[], remove_questions=[])
        if "message" in response:
            return jsonify(response),200
    except Exception as e:
    # return jsonify(error="Failed to create exam"),500
        return jsonify(error=f"Failed to update exam: {str(e)}"), 500
        
@exams_views.route('/api/add_question_to_exam/<int:exam_id>', methods=['PUT'])
@login_required
def user_api_add_question_to_exam_details(exam_id):
    try:
        teacher = current_user
        data = request.json
        if not data  or 'course_code' not in data:
            return jsonify({'error':'Missing required data'}), 400
        if not teacher:
            return jsonify({'error':'Unauthorized'}), 401
        exam_id_list = [e.id for e in teacher.my_exams]
        if exam_id not in exam_id_list:
            return jsonify({'error':'Unauthorized'}), 401
        add_list = []
        question_1 =  save_question(teacherId=teacher.id, text=data['new_question_text'], difficulty=data['new_question_difficulty'], courseCode=data['course_code'], options=[])
        if not question_1:
            return jsonify({'error':'Failed to save question 1'}), 400
        option_1 = create_option(question_id=question_1.id, body=data['option_1'], image=None, is_correct=False)
        option_2 = create_option(question_id=question_1.id, body=data['option_2'], image=None, is_correct=False)
        option_3 = create_option(question_id=question_1.id, body=data['option_3'], image=None, is_correct=True)
        option_4 = create_option(question_id=question_1.id, body=data['option_4'], image=None, is_correct=False)
        if not option_1 or not option_2 or not option_3 or not option_4:
            return jsonify({'error':'Failed to save options'}), 400
        associate_option(question_1.id, option_1) 
        associate_option(question_1.id, option_2) 
        associate_option(question_1.id, option_3) 
        associate_option(question_1.id, option_4)
        add_list.append(question_1.id)
        exam = get_exam_and_return_exam(exam_id)
        if add_questions(id=exam_id,question_ids=add_list):
            response = {"message": "Question added successfully", "exam": exam.get_json()}
            return jsonify(response), 200
    except Exception as e:
    # return jsonify(error="Failed to create exam"),500
        return jsonify(error=f"Failed to add question to  exam: {str(e)}"), 500
# remove a questio
#   remove_list = []
# remove_question = exam.exam_questions[0]
# remove_list.append(remove_question.id)
@exams_views.route('/api/remove_question_from_exam/<int:exam_id>', methods=['PUT'])
@login_required
def user_api_remove_question_from_exam(exam_id):
    try:
        teacher = current_user
        if not teacher:
            return jsonify({'error':'Unauthorized'}), 401
        exam_id_list = [e.id for e in teacher.my_exams]
        if exam_id not in exam_id_list:
            return jsonify({'error':'Unauthorized'}), 401
        exam = get_exam_and_return_exam(exam_id)
        remove_list = []
        remove_question = exam.exam_questions[0]
        remove_list.append(remove_question.id)
        response = update_exam(exam_id=exam_id,title=None, course_code=None, add_questions=[], remove_questions=remove_list)
        if "message" in response:
            updated_exam = get_exam_and_return_exam(exam_id)
            new_response = {"message": "Question removed successfully", "exam": updated_exam.get_json()}
            return jsonify(new_response),200
    except Exception as e:
    # return jsonify(error="Failed to create exam"),500
        return jsonify(error=f"Failed to remove question from  exam: {str(e)}"), 500
    

@exams_views.route('/api/save_exam/<int:exam_id>', methods=['PUT'])
@login_required
def user_api_save_exam(exam_id):
    try:
        teacher = current_user
        if not teacher:
            return jsonify({'error':'Unauthorized'}), 401
        exam_id_list = [e.id for e in teacher.my_exams]
        if exam_id not in exam_id_list:
            return jsonify({'error':'Unauthorized'}), 401
        response = save_exam(exam_id=exam_id)
        if "message" in response:
            return jsonify(response),200
    except Exception as e:
        return jsonify(error=f"Failed to save exam: {str(e)}"), 500
        
@exams_views.route('/api/get_teacher_exams', methods=['GET'])
@login_required
def user_api_get_exams():
    try:
        teacher = current_user
        if not teacher:
            return jsonify({'error':'Unauthorized'}), 401
        exams = myExams(id=teacher.id)
        if not exams:
            return jsonify({'message':'No exams found'}), 404
        exams_json = [exam.get_json() for exam in exams]
        return jsonify(exams_json), 200
    except Exception as e:
        return jsonify(error=f"Error: {str(e)}"), 500

    
    
        
        

