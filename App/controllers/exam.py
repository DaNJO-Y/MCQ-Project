from App.models import Exam
from App.models import Question
from App.database import db
from flask import send_file
from fpdf import FPDF
import os
import random
from io import BytesIO
from flask import Response

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

def download_exam(exam_id, format):
    exam = Exam.query.get(exam_id)
    if not exam:
        return {"error": "Exam not found"}, 404

    if format == "txt":
        # Create the file in memory
        file_content = f"Exam Title: {exam.title}\n"
        file_content += f"Course Code: {exam.course_code}\n"
        file_content += "Questions:\n"
        for index, question in enumerate(exam.exam_questions, start=1):
            file_content += f"{index}. {question.text}\n"

        # Use BytesIO to create a file-like object
        file_stream = BytesIO(file_content.encode('utf-8'))
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=f"exam_{exam.id}.txt",
            mimetype="text/plain"
        )

    elif format == "pdf":
        # Create the PDF in memory
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add exam details
        pdf.cell(200, 10, txt=f"Exam Title: {exam.title}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Course Code: {exam.course_code}", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt="Questions:", ln=True)
        pdf.ln(5)

        # Debugging: Print questions to console
        print(f"Exam Title: {exam.title}")
        print(f"Course Code: {exam.course_code}")
        print("Questions associated with this exam:")
        for question in exam.exam_questions:
            print(f"Question ID: {question.id}, Text: {question.text}")

        # Add questions to the PDF
        for index, question in enumerate(exam.exam_questions, start=1):
            pdf.multi_cell(0, 10, f"{index}. {question.text}")

        # Use BytesIO to create a file-like object
        file_stream = BytesIO()
        pdf.output(file_stream)
        file_stream.seek(0)  # Move to the beginning of the file stream

        # Send the file to the user
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=f"exam_{exam.id}.pdf",
            mimetype="application/pdf"
        )

    else:
        return {"error": "Invalid format. Use 'txt' or 'pdf'."}, 400

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

    print(f"Exam ID: {exam.id}, Title: {exam.title}")
    print("Questions:")
    for question in exam.exam_questions:
        print(f"Question ID: {question.id}, Text: {question.text}")

    return {"message": "Questions shuffled successfully", "exam": exam.get_json()}