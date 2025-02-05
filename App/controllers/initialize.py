from .user import create_user, get_user_by_username
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('Robert','Manage','bob','bobpass','bob@email.com')
    user = get_user_by_username('bob')
    # user_type = user.type
    # print(user_type)
