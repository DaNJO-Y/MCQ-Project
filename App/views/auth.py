from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies


from.index import index_views

from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/home')
def home_page():
  return render_template('layout.html')

@auth_views.route('/base')
@jwt_required()
def base_page():
  user = current_user
  return render_template('home.html', user=user)

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    
    #response = redirect(request.referrer)
    
    if not token:
        flash('Bad username or password given'), 401
        return redirect(url_for('auth_views.home_page'))
    else:
        flash('Login Successful')
        response = redirect(url_for('auth_views.base_page'))
        access_token = create_access_token(identity=user.i)
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
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
  # newUser = User(email=data['email'], username=data['username'], password=data['password'])
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