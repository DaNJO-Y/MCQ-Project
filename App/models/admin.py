from .user import User
from App.database import db
from flask_login import UserMixin

class Admin(User, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    #add details here

    __mapper_args__ = {
        'polymorphic_identity': 'Admin'
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

    def __repr__(self):
        return (
            f"User-ID(userId={self.id}, firstName='{self.firstName}', "
            f"lastName='{self.lastName}', email='{self.email}', username='{self.username}')"
        )

   