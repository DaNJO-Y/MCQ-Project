from .teacher import Teacher
from .exam import Exam
from .tag import Tag
from App.database import db

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    teacherId = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    examId = db.Column(db.Integer, db.ForeignKey('exam.id'))
    # tagId = db.Column(db.Integer, db.ForeignKey('tag.id'))
    correctOption = db.relationship('Option', backref=db.backref('question_correct_option', lazy='joined'))
    # teacher = db.relationship('Teacher', backref=db.backref('question', lazy='joined'))
    image = db.Column(db.String(300))
    difficulty = db.Column(db.String(200))
    tag = db.relationship('Tag', secondary='question_tag_bridge', back_populates = 'question')
    courseCode = db.Column(db.String(200))
    belonging_exams = db.relationship('Exam', secondary='exam_question', back_populates='exam_questions', lazy='joined')
    statistics = db.relationship('QuestionStatistics', backref=db.backref('question_statistics', lazy='joined'))
    options = db.relationship('Option', back_populates='question')
    lastUsed = db.Column(db.Date, nullable=True)
# =======
#     exams = db.relationship('Exam', secondary='exam_question', back_populates='questions', lazy='joined')
#     statistics = db.relationship('QuestionStatistics', backref=db.backref('question_stats',lazy='joined'))
#     options = db.relationship('Option', back_populates = 'question')
#     lastUsed = db.Column(db.Date, nullable = True)
# >>>>>>> main

    def __init__(self, teacherId, correctOption, difficulty, courseCode, options):
        self.teacherId = teacherId
        self.correctOption = correctOption
        self.difficulty = difficulty
        self.courseCode = courseCode
        self.options = options

    def get_json(self):
        return {
            "id": self.id,
            "teacherid": self.teacherId,
            "correct option":self.correctOption,
            "difficulty": self.difficulty,
            "course code":self.courseCode,
            "options":[options for op in self.options]
        }

