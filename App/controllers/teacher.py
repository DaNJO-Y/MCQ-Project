from App.models import Teacher
from App.database import db

def create_teacher(firstName, lastName, username, password, email):
    newteacher = Teacher(firstName=firstName, lastName=lastName, username=username, password=password, email=email)
    db.session.add(newteacher)
    db.session.commit()
    return newteacher

def get_teacher_by_username(username):
    return Teacher.query.filter_by(username=username).first()

def get_teacher(id):
    return teacher.query.get(id)

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

def update_teacher(id, username):
    teacher = get_teacher(id)
    if teacher:
        teacher.username = username
        db.session.add(teacher)
        return db.session.commit()
    return None