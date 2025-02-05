from App.database import db

class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    #add details here

    __mapper_args__ = {
        'polymorphic_identity': 'teacher'
    }

    def __init__(self, firstName, lastName, username, password, email):
        super().__init__(firstName, lastName, username, password, email, type='teacher')

    def get_json(self):
        return{
            'id': self.id,
            'firstName':self.firstName,
            'lastName' :self.lastName,
            'email':self.email
        }