from .user import User
from App.database import db
from flask_login import UserMixin

class Tutor(User, UserMixin):
    __tablename__ = 'tutor'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    #add details here

    __mapper_args__ = {
        'polymorphic_identity': 'tutor'
    }

    def __init__(self, firstName, lastName, username, password, email):
        super().__init__(firstName, lastName, username, password, email, type='tutor')

    def get_json(self):
        return{
            'id': self.id,
            'firstName':self.firstName,
            'lastName' :self.lastName,
            'email':self.email
        }