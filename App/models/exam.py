from App.database import db
from sqlalchemy.sql import func
from .exam_question import exam_question

class Exam(db.Model):
    __tablename__ = 'exam'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    title = db.Column(db.String(120), unique=True, nullable=False)
    course_code = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=func.now(), nullable=False)
    saved = db.Column(db.Boolean, default=False)

    teacher = db.relationship('Teacher', back_populates='my_exams')
    exam_questions = db.relationship('Question', secondary='exam_question', back_populates='belonging_exams')
    statistics = db.relationship('ExamStatistics', back_populates='exam', lazy=True, cascade="all, delete-orphan")


 
    def __init__(self, teacher_id, title, course_code):
        self.teacher_id = teacher_id
        self.title = title
        self.course_code = course_code
        self.saved = False


    def get_json(self):
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "title": self.title,
            "course_code": self.course_code,
            "saved": self.saved,
            "questions": [question.id for question in self.exam_questions],
            "statistics": [stat.get_json() for stat in self.statistics] if self.statistics else []
        }
