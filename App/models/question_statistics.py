from .question import Question
from App.database import db

class QuestionStatistics(db.Model):
    __tablename__ = 'question_statistics'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    data = db.Column(db.String(255), nullable=False)
    year =db.Column(db.Integer, nullable=False)

    question = db.relationship('Question', back_populates='statistics') # Use back_populates

    def __init__(self, question_id, data, year):
        self.question_id = question_id
        self.data = data
        self.year = year

    def get_json(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "year": self.year
        }