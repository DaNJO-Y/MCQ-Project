from App.database import db

class ExamQuestion(db.Model):
    __tablename__ = 'exam_question'
    
  
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True, nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), primary_key=True, nullable=False)


    def __init__(self, exam_id, question_id):
        self.exam_id = exam_id
        self.question_id = question_id

 
    def get_json(self):
        return {
            "exam_id": self.exam_id,
            "question_id": self.question_id
        }

