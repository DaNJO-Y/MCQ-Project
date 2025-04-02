from App.models import Teacher
from App.models import Question
from App.models import Exam
from App.controllers import *
from App.database import db
from datetime import date

def create_teacher(firstName, lastName, username, password, email):
    newteacher = Teacher(firstName=firstName, lastName=lastName, username=username, password=password, email=email)
    db.session.add(newteacher)
    db.session.commit()
    return newteacher

def is_teacher(id):
    user = get_teacher(id)
    if not user:
        return None
    user_type = user.type
    if user_type == "teacher":
        return user     

def get_teacher_by_username(username):
    return Teacher.query.filter_by(username=username).first()

def get_teacher(id):
    return Teacher.query.get(id)

def get_teacher_json(id):
    teacher = Teacher.query.get(id)
    return teacher.get_json()


def get_all_teacher():
    return Teacher.query.all()

def get_all_teacher_json():
    teachers = Teacher.query.all()
    if not teachers:
        return []
    teachers = [teacher.get_json() for teacher in teachers]
    return teachers

def update_teacher(id, username, email):
    teacher = get_teacher(id)
    if teacher:
        teacher.username = username
        teacher.email = email
        db.session.add(teacher)
        return db.session.commit()
    return None

def addQuestion(teacher_id,question,exam_id):
    teacher = get_teacher(teacher_id)
    if teacher:
        if question.teacher_id == teacher.id:
            exam = get_exam_by_id(exam_id)
            if exam.teacher_id == teacher.id:
                exam.exam_questions.append(question)
                db.session.add(exam)
                return db.session.commit
    return None

def createExam(teacher_id, title, courseCode):
    teacher = get_teacher(teacher_id)
    if teacher:
        new_Exam = Exam(teacher_id=teacher.id, title=title, course_code=courseCode)
        new_Exam.date_created = date.today()
        db.session.add(new_Exam)
        teacher.my_exams.append(new_Exam)
        db.session.commit()
    return new_Exam

def createQuestion(teacher_id, text, difficulty, courseCode, options):
    teacher = get_teacher(id)
    if teacher:
      new_Question = save_question(teacherId=teacher_id, text=text, difficulty=difficulty,courseCode=courseCode, options=options)
      teacher.questions.append(new_Question)
      db.session.add(teacher)
      return db.session.commit()
    return None  
    

def myExams(id):
    teacher = get_teacher(id)
    if teacher:
        return teacher.exams
    return None

def myQuestions(id):
    teacher = get_teacher(id)
    if teacher:
        return teacher.questions
    return None