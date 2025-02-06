from App.models import Admin
from App.database import db

def create_admin(firstName, lastName, username, password, email):
    newadmin = Admin(firstName=firstName, lastName=lastName, username=username, password=password, email=email)
    db.session.add(newadmin)
    db.session.commit()
    return newadmin

def get_admin_by_username(username):
    return Admin.query.filter_by(username=username).first()

def get_admin(id):
    return Admin.query.get(id)

def get_admin_json(id):
    admin = Admin.query.get(id)
    return admin.get_json()


def get_all_admin():
    return Admin.query.all()

def get_all_admin_json():
    admins = Admin.query.all()
    if not admins:
        return []
    admins = [admin.get_json() for admin in admins]
    return admins

def update_admin(id, username):
    admin = get_admin(id)
    if admin:
        admin.username = username
        db.session.add(admin)
        return db.session.commit()
    return None