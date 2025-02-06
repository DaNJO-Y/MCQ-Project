from .user import create_user, get_user_by_username, get_all_users
from .admin import *
from .teacher import *
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('Robert','Manage','bob','bobpass','bob@email.com')
    create_admin('Patty', 'Lenain', 'pat', 'patpass','pat@email.com')
    create_teacher('Andrew', 'Vin', 'drew', 'drewpass', 'drew@email.com')
    user = get_user_by_username('bob')
    admin = get_admin_by_username('pat')
    teacher = get_teacher_by_username('drew')
    user_type = user.type
    admin_type = admin.type
    teacher_type = teacher.type
    user = is_teacher(teacher.id)
    if user:
        print(user.type)
    
    user2 = is_admin(teacher.id)
    if not user2:
        print(f'user is not an admin')
    #print(user2.type)
    #print(admin_type)
    #print(teacher_type)
    #print(get_teacher_json(teacher.id))
    #print(get_all_users())
    #print(get_all_admin())
