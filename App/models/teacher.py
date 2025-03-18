from .user import User
from App.database import db
from flask_login import UserMixin

class Teacher(User, UserMixin):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    exams = db.relationship('Exam', back_populates='teacher')
    questions = db.relationship('Question', backref=db.backref('teacher',lazy='joined'))
    #add details here

    __mapper_args__ = {
        'polymorphic_identity': 'teacher'
    }

    def __init__(self, firstName, lastName, username, password, email):
        super().__init__(firstName, lastName, username, password, email)

    def get_json(self):
        return{
            'id': self.id,
            'firstName':self.firstName,
            'lastName' :self.lastName,
            'email':self.email
    }

    def __str__(self):
        return (
            f"FirstName={self.firstName}, "
            f"LastName={self.lastName}, "
            f"Email={self.email}"
        )
    
    def __repr__(self):
        return (
            f"FirstName: '{self.firstName}' | "
            f"LastName: '{self.lastName}'  |"
            f"Email={self.email}"
        )