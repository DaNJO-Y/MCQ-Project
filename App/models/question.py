from .teacher import Teacher
from .exam import Exam
from App.database import db

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    teacherId = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    examId = db.Column(db.Integer, db.ForeignKey('exam.id'))
    correctOption = db.relationship('Option', backref=db.backref('question', lazy='joined'))
    # teacher = db.relationship('Teacher', backref=db.backref('question', lazy='joined'))
    image = db.Column(db.String(300))
    difficulty = db.Column(db.String(200))
    tag = db.relationship('Tag', backref=db.backref('Tag', secondary='question_tag_bridge', backref=db.backref('question',lazy=True)))
    courseCode = db.Column(db.String(200))
    exams = db.relationship('Exam', backref=db.backref('question',lazy='joined'))
    statistics = db.relationship('QuestionStatistics', backref=db.backref('question_stats',lazy='joined'))
    options = db.relationship('Option', backref=db.backref('question', lazy='joined'))
    lastUsed = db.Column(db.Date, nullable = True)

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

