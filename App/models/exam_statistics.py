from App.database import db

class ExamStatistics(db.Model):
    __tablename__ = 'exam_statistics'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    data = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)


    exam = db.relationship('Exam', back_populates='statistics')


    def __init__(self, exam_id, data, year):
        self.exam_id = exam_id
        self.data = data
        self.year = year


    def get_json(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "data": self.data,
            "year": self.year
        }
