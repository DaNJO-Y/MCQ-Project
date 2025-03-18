from .question import Question
from App.database import db

class Option(db.Model):
    __tablename__='option'
    id = db.Column(db.Integer, primary_key=True)
    questionId = db.Column(db.Integer, db.ForeignKey('question.id'))
    body = db.Column(db.String(300))
    image = db.Column(db.String(300))
    question = db.relationship('Question', backref=db.backref('option', lazy='joined'))

    def __init__(self, questionId, body=None, image=None):
        self.questionId =questionId
        self.body = body
        self.image = image

    def get_json(self):
        return{
            "id":self.id,
            "questionId":self.questionId,
            "body":self.body
        }