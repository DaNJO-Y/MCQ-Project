from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from.index import index_views

from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    


@auth_views.route('/homePage',methods=['GET'])
def homePage():
    return render_template('homepage.html')


@auth_views.route('/identify', methods=['GET'])
# @jwt_required()
@login_required
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    username = data['username']
    password = data['password']
    potential_teacher = get_teacher_by_username(username)
    potential_admin = get_admin_by_username(username)
    user = get_user_by_username(username)
    if potential_teacher and check_password_hash(potential_teacher.password,password):
        login_user(potential_teacher,remember=True)
        flash(f'Login Successful! Welcome {user.firstName}')
        return redirect(url_for('auth_views.homePage'))
    elif potential_admin and check_password_hash(potential_admin.password,password):
        login_user(potential_admin,remember=True)
        flash(f'Login Successful! Welcome {user.firstName}')
        return redirect(url_for('auth_views.homePage'))
    elif user and check_password_hash(user.password,password):
        login_user(user,remember=True)
        flash(f'Login Successful! Welcome {user.firstName}')
        return redirect(url_for('auth_views.homePage'))
    else:
        flash('Bad username or password given')
        return render_template('login.html'), 401

@auth_views.route('/logout', methods=['GET'])
# @jwt_required()
@login_required
def logout_action():
    response = redirect(url_for('auth_views.home_page')) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    logout_user()
    return response

@auth_views.route('/signup')
def signup_action():
    return render_template('signup.html')

@auth_views.route('/signupadmin')
#def signup_admin():


@auth_views.route('/signup', methods=['POST'])
def signup_action_data():
  data = request.form
  response = None
  if data['radio'] == 'admin':
    newUser = create_admin(data['first_name'], data['last_name'], data['username'],data['pwd'], data['email'])
    response = redirect(url_for('auth_views.home_page'))
  elif data['radio'] == 'teacher':
    newUser = create_teacher(data['first_name'], data['last_name'], data['username'],data['pwd'], data['email'])
    response = redirect(url_for('auth_views.home_page'))
  else:
    newUser = create_user(data['first_name'], data['last_name'], data['username'],data['pwd'], data['email'])
    response = redirect(url_for('auth_views.home_page'))
    try:
      db.session.add(newUser)
      db.session.commit()
      token = login_user(data['username'], data['password'])
      set_access_cookies(response, token)
      flash('Account created!')
    except Exception:
      db.session.rollback()
      app.logger.error(f"Error occurredd: {e}")
      flash("username or email already exists")  
      response = redirect(url_for('login'))
  return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response




# @auth_views.route('/admin_home')
# def admin_home_page():
#   return render_template('admin.html')

# @auth_views.route('/aHome')
# @login_required
# def is_admin():
#   user = current_user
#   if user.type != 'Admin':
#     flash("You are not authorized to view the admin page")
#     response = redirect(url_for('auth_views.base_page'))
#   if user.type == 'Admin':
#     response = redirect(url_for('auth_views.admin_home_page'))
#   return response

# @auth_views.route('/base')
# @login_required
# def base_page():
#   user = current_user
#   if user.type == 'Admin':
#     title = "Admin"
#     message=f"Hello you are a {current_user.type}"
#   if user.type == 'teacher':
#     title = "Teacher"
#     message=f"Hello you are a {current_user.type}"
#   if user.type == 'user':
#     title = "User"
#     message=f"Hello you are a {current_user.type}"
#   return render_template('home.html',title=title, message=message, current_user=current_user,)

# @auth_views.route('/users', methods=['GET'])
# def get_user_page():
#     users = get_all_users()
#     return render_template('users.html', users=users)