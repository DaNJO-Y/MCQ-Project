from App.models import Exam
from App.models import Question
from App.database import db
from flask import send_file
#from fpdf2 import FPDF
import os
import random

def create_exam(title, course_code, questions, teacher_id):
    # Create a new exam instance
    new_exam = Exam(title=title, course_code=course_code, teacher_id=teacher_id)

    # Add questions to the exam
    for question in questions:
        question_instance = Question.query.get(question)
        if question_instance:
            new_exam.questions.append(question_instance)

    db.session.add(new_exam)
    db.session.commit()
    return new_exam.get_json()  # Return the created exam as JSON

def get_exams(user, page=1, per_page=10):
    paginated_exams = Exam.query.filter_by(teacher_id=user.id).paginate(page=page, per_page=per_page, error_out=False)

    if paginated_exams.items:
        return {
            "exams": [exam.get_json() for exam in paginated_exams.items],  
            "total_exams": paginated_exams.total,  
            "current_page": paginated_exams.page,  
            "total_pages": paginated_exams.pages, 
            "per_page": paginated_exams.per_page 
        }
    
    return {"message": "No exams found"}, 404


def get_exam_by_id(exam_id):
    exam = Exam.query.get(exam_id)  # Fix: Corrected typo from `quesy` to `query`
    if exam:
        return exam.get_json()
    return {"error": "Exam not found"}, 404


def delete_exam(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404
    db.session.delete(exam)
    db.session.commit()
    return {"message": "Exam deleted successfully"}


def edit_exam(exam_id, title=None, course_code=None, add_questions=None, remove_questions=None):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404

    # Update Exam Title or Course Code 
    if title:
        exam.title = title
    if course_code:
        exam.course_code = course_code

    #Add Questions 
    if add_questions:
        for question_id in add_questions:
            question = Question.query.get(question_id)
            if question and question not in exam.questions:
                exam.questions.append(question)  # Add question to exam

    # Remove Questions
    if remove_questions:
        for question_id in remove_questions:
            question = Question.query.get(question_id)
            if question and question in exam.questions:
                exam.questions.remove(question)  # Remove question from exam

    db.session.commit()  
    return exam.get_json()  


def download_exam(exam_id, format="txt"):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404

    filename = f"exam_{exam.id}.{format}"
    filepath = os.path.join("downloads", filename)

    # Ensure the downloads directory exists
    os.makedirs("downloads", exist_ok=True)

    if format == "txt":
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"Exam Title: {exam.title}\n")
            file.write(f"Course Code: {exam.course_code}\n")
            file.write("Questions:\n")
            for index, question in enumerate(exam.questions, start=1):
                file.write(f"{index}. {question.text}\n")
    
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Exam Title: {exam.title}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Course Code: {exam.course_code}", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt="Questions:", ln=True)
        pdf.ln(5)
        
        for index, question in enumerate(exam.questions, start=1):
            pdf.multi_cell(0, 10, f"{index}. {question.text}")
        
        pdf.output(filepath)

    else:
        return {"error": "Invalid format. Use 'txt' or 'pdf'."}, 400

    return send_file(filepath, as_attachment=True)


def save_exam(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404

    exam.saved = True  
    db.session.commit()

    return {"message": "Exam saved successfully", "exam": exam.get_json()}


def shuffle_questions(exam_id):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404

    # Shuffle questions
    questions_list = exam.questions[:]  # Copy the list
    random.shuffle(questions_list)

    # Update the exam's question order
    exam.questions = questions_list
    db.session.commit()

    return {"message": "Questions shuffled successfully", "exam": exam.get_json()}