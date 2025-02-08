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
@auth_views.route('/home')
def home_page():
  return render_template('index.html')

@auth_views.route('/base')
@login_required
def base_page():
  user = current_user
  if user.type == 'Admin':
    title = "Admin"
    message=f"Hello you are a {current_user.type}"
  if user.type == 'teacher':
    title = "Teacher"
    message=f"Hello you are a {current_user.type}"
  if user.type == 'user':
    title = "User"
    message=f"Hello you are a {current_user.type}"
  return render_template('home.html',title=title, message=message, current_user=current_user,)

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

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
    if not potential_teacher == None:
      if check_password_hash(potential_teacher.password,password):
        response = redirect(url_for('auth_views.base_page'))
        login_user(potential_teacher,remember=True)
        flash('Login Successful')
        return response
    elif not potential_admin == None:
      if check_password_hash(potential_admin.password,password):
        response = redirect(url_for('auth_views.base_page'))
        login_user(potential_admin,remember=True)
        flash('Login Successful')
        return response
    elif not user == None:
      if check_password_hash(user.password,password):
        response = redirect(url_for('auth_views.base_page'))
        login_user(user,remember=True)
        flash('Login Successful')
        return response
    else:
        flash('Bad username or password given'), 401
        return redirect(url_for('auth_views.home_page'))


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
    try:
      db.session.add(newUser)
      db.session.commit()
      token = login_user(data['username'], data['password'])
      response = redirect(url_for('auth_views.login_action'))
      set_access_cookies(response, token)
      flash('Account created!')
    except Exception:
      db.session.rollback()
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