from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from sqlalchemy_serializer import SerializerMixin

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(120), nullable = False)
    lastName = db.Column(db.String(120), nullable = False)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)


    #type of user
    type = db.Column(db.String(120))

    __mapper_args__={
        'polymorphic_identity': 'user',
        'polymorphic_on': 'type'
    }

    def __init__(self, firstName, lastName, username, password, email):
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.set_password(password)
        self.email = email
        
    def get_json(self):
        return{
            'id': self.id,
            'firstName':self.firstName,
            'lastName':self.lastName,
            'username': self.username,
            'email': self.email
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return (
            f"User-ID(userId={self.id}, firstName='{self.firstName}', "
            f"lastName='{self.lastName}', email='{self.email}', username='{self.username}')"
        )

# pip install sqlalchemy-serializer