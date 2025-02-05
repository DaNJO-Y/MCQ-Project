from App.database import db

class Admin(User):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    #add details here

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def __init__(self, firstName, lastName, username, password, email):
        super().__init__(firstName, lastName, username, password, email, type='admin')

    def get_json(self):
        return{
            'id': self.id,
            'firstName':self.firstName,
            'lastName' :self.lastName,
            'email':self.email
        }

   