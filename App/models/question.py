from .teacher import Teacher
from .exam import exam_question
from .associations import Question_Tag_Bridge
from App.database import db

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    teacherId = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    examId = db.Column(db.Integer, db.ForeignKey('exam.id'))
    text = db.Column(db.String(500))
    image = db.Column(db.String(300))
    difficulty = db.Column(db.String(200))
    tag = db.relationship('Tag', secondary='question_tag_bridge', back_populates='question')
    courseCode = db.Column(db.String(200))
    belonging_exams = db.relationship('Exam', secondary='exam_question', back_populates='exam_questions', lazy='joined')
    statistics = db.relationship('QuestionStatistics', back_populates='question') # Use back_populates
    options = db.relationship('Option', back_populates='question')
    lastUsed = db.Column(db.Date, nullable=True)
    dateCreated = db.Column(db.Date, nullable= True)

    def __init__(self, teacherId, text, difficulty, courseCode, options):
        self.teacherId = teacherId
        self.text = text
        self.difficulty = difficulty
        self.courseCode = courseCode
        self.options = options

    def get_json(self):
        return {
            "id": self.id,
            "teacherid": self.teacherId,
            "text": self.text,
            "difficulty": self.difficulty,
            "course code": self.courseCode,
            "options": [op.get_json() for op in self.options]
        }
    