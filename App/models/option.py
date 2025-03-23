from .question import Question
from App.database import db

class Option(db.Model):
    __tablename__='option'
    id = db.Column(db.Integer, primary_key=True)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    body = db.Column(db.String(300))
    image = db.Column(db.String(300))
    is_correct = db.Column(db.Boolean, default=False)
    question = db.relationship('Question', back_populates='options')

    def __init__(self, questionId, body=None, image=None, is_correct=False):
        self.questionId =questionId
        self.body = body
        self.image = image
        self.is_correct = is_correct

    def get_json(self):
        return{
            "id":self.id,
            "questionId":self.questionId,
            "body":self.body,
            "is_correct": self.is_correct
        }
    def toggle(self):
        self.is_correct = not self.is_correct
        