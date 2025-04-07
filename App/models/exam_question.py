from App.database import db

class ExamQuestion(db.Model):
    __tablename__ = 'exam_question'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)


    def __init__(self, exam_id, question_id):
        self.exam_id = exam_id
        self.question_id = question_id

 
    def get_json(self):
        return {
            "exam_id": self.exam_id,
            "question_id": self.question_id
        }

