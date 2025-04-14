from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for, session
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from App.controllers import teacher 
from App.models import *
from flask_mail import Mail, Message
from flask import current_app
import os
import uuid
import json
from.index import index_views
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyotp
import threading
import sendgrid, time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from App.controllers import *

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

# app = Flask(__name__)  # Replace with your actual app initialization
# app.config['UPLOAD_FOLDER'] = 'uploads'  # Set your upload folder
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# def save_image(file):
#     if file:
#         try:
#             filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             return filename
#         except Exception as e:
#             print(f"Error saving image: {e}")
#             return None
#     return None

def generate_secret_key():
    return pyotp.random_base32()

def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

def verify_otp(secret_key, otp):
    totp = pyotp.TOTP(secret_key)
    # print(f"Verifying with Secret Key: {secret_key}")
    # print(f"Verifying OTP: {otp}")
    return totp.verify(otp, valid_window=4)


def send_email(otp, user_email):
    message = Mail(
    from_email='d4884781@gmail.com',
    to_emails=[user_email],
    subject='This e-mail message is being sent to deliver your one-time password.',
    html_content=f'<strong>This is your one-time password code: {otp} .</strong>')
    try:
        sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
            print(f"Error sending email: {str(e)}")

RESEND_LIMIT = 3  
RESEND_WINDOW = 60  
resend_attempts = {}
# secret_key= ""
otp = ""

'''
Page/Action Routes
'''    

@auth_views.route('/homePage',methods=['GET'])
def homePage():
    return render_template('homepage.html')

@auth_views.route('/otp', methods=['GET'])
def otp_page():
    return render_template('otp.html')


@auth_views.route('/identify', methods=['GET'])
# @jwt_required()
@login_required
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/resend',methods=['POST'])
def resend_code():
    data = request.form
    email = data['email']
    now = time.time()
    otp=""
    session.pop('secret_key', None)

    if email in resend_attempts and resend_attempts[email]['count'] >= RESEND_LIMIT and now - resend_attempts[email]['last_request'] < RESEND_WINDOW:
        flash(f"Too many resend requests. Please wait {RESEND_WINDOW - int(now - resend_attempts[email]['last_request'])} seconds before trying again.", 'error')
        return render_template('otp.html', email=email)

    secret_key = generate_secret_key()
    # print(f'this is the : {secret_key}')
    session['secret_key'] = secret_key  # Store in session
    otp = generate_otp(secret_key)
    # print(f"Generated OTP: {otp}")
    send_email(otp,email)
    flash("New OTP sent to your email address.")
    if email not in resend_attempts or now - resend_attempts[email]['last_request'] > RESEND_WINDOW:
        resend_attempts[email] = {'count': 1, 'last_request': now}
    else:
        resend_attempts[email]['count'] += 1
        resend_attempts[email]['last_request'] = now
    
    return render_template('otp.html', email=email)


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    username = data['username']
    password = data['password']
    potential_teacher = teacher.get_teacher_by_username(username)
    potential_admin = get_admin_by_username(username)
    user = get_user_by_username(username)
    if potential_teacher and check_password_hash(potential_teacher.password,password):
        login_user(potential_teacher,remember=True)
        flash(f'Login Successful! Welcome {potential_teacher.firstName}')
        secret_key = generate_secret_key()
        print(f'this is the : {secret_key}')
        session['secret_key'] = secret_key  # Store in session
        otp = generate_otp(secret_key)
        print(f"Generated OTP: {otp}")
        send_email(otp,potential_teacher.email)
        # return redirect(url_for('auth_views.homePage'))
        return render_template('otp.html', email=potential_teacher.email)
        # return render_template('login.html', twoFactor = True)
    elif potential_admin and check_password_hash(potential_admin.password,password):
        login_user(potential_admin,remember=True)
        flash(f'Login Successful! Welcome {potential_admin.firstName}')
        return render_template('otp.html')
        # return redirect(url_for('auth_views.homePage'))
    elif user and check_password_hash(user.password,password):
        login_user(user,remember=True)
        flash(f'Login Successful! Welcome {user.firstName}')
        # return redirect(url_for('auth_views.homePage'))
        return render_template('otp.html')
        # return render_template('login.html', twoFactor = True), 401
    else:
        flash('Bad username or password given')
        return render_template('login.html', twoFactor = False), 401

@auth_views.route('/authenticate', methods=['POST'])
def auth_user():
    data = request.form
    one_time_pad = data['otp']
    secret_key = session.pop('secret_key', None)
    print(f'hiiii this is the : {secret_key}')
    print(one_time_pad)
    print("hi")
    # user_input_otp = input("Enter OTP: ")
    if secret_key and verify_otp(secret_key, one_time_pad):
        flash("OTP verified. Access granted.")
        return redirect(url_for('auth_views.homePage'))
    else:
        flash("OTP verification failed. Access denied.")
        return render_template('login.html')


@auth_views.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_views.route('/logout', methods=['GET'])
# @jwt_required()
@login_required
def logout_action():
    response = redirect(url_for('auth_views.login_page')) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    logout_user()
    return response

@auth_views.route('/signup')
def signup_action():
    return render_template('signupPage.html')

@auth_views.route('/signupadmin')
#def signup_admin():


@auth_views.route('/signup', methods=['POST'])
def signup_action_data():
    data = request.form
    response = None
    email = data['email']
    username = data['username']
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email address already exists. Please use a different email.")
        return redirect(url_for('auth_views.signup_action_data'))

    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        flash("Username already exists. Please use a different username.")
        return redirect(url_for('auth_views.signup_action_data'))
    new_user = teacher.create_teacher(data['first_name'], data['last_name'], data['username'], data['pwd'], email)

# try:
#     if data['radio'] == 'admin':
#         new_user = create_admin(data['first_name'], data['last_name'], data['username'], data['pwd'], email)
#     elif data['radio'] == 'teacher':
#         new_user = teacher.create_teacher(data['first_name'], data['last_name'], data['username'], data['pwd'], email)
#     else:
#         new_user = create_user(data['first_name'], data['last_name'], data['username'], data['pwd'], email)

    db.session.add(new_user)
    db.session.commit()

        # Assuming login_user is defined elsewhere and works correctly
    login_user(new_user, remember=True)

    flash('Account created!')
    response = render_template('login.html')

    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(f"Error occurred: {e}")
    #     flash("An error occurred during signup. Please try again.")
    #     response = redirect(url_for('auth_views.signup_action_data')) #redirect to signup page.

    return response

'''
API Routes
'''
def get_token(user):
    login_user(user)
    access_token = create_access_token(identity=user.id)
    return access_token

def login_user_token(username,password):
    teacher = get_teacher_by_username(username)
    if teacher and check_password_hash(teacher.password,password):
        return get_token(teacher)

@auth_views.route('/api/login', methods=['POST'])
def user_api_login():
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error":"Username and Password required"}), 400
        token = login_user_token(data['username'], data['password'])
        if not token:
            return jsonify({"error": "Bad Username or Password Given"}), 401
        return jsonify(access_token=token), 200
    except Exception as e:
        return jsonify(error="An Error Occurred While Logging In"), 500
        
@auth_views.route('/api/signup', methods=['POST'])
def user_api_signup():
    try:
        data = request.json
        if not data or 'firstname' not in data or 'lastname' not in data or 'username' not in data or 'email' not in data or 'password' not in data or 'type' not in data:
            return jsonify({"error":"Required fields missing"}), 400
        if data['type'] == 'teacher':
            user = create_teacher(data['firstname'], data['lastname'], data['username'], data['password'], data['email'])
            if user:
                return jsonify({"message": f"{data['firstname']} has been created in the system"}), 200
        if data['type'] != 'teacher':
            return jsonify({"error":"The system only handles teachers"}),401
    except Exception as e:
        return jsonify(error="An Error Occurred While Signing up"), 500
    
@auth_views.route('/api/logout', methods=['POST'])
@login_required
def user_api_logout():
    user = current_user
    try:
        response = jsonify(message=f"{user.username} has been logged out successfully")
        unset_jwt_cookies(response)
        logout_user()
        return response,200
    except Exception as e:
        return jsonify(error="An Error Occurred While Logging out"), 500


# @auth_views.route('/api/login', methods=['POST'])
# def user_login_api():
#   data = request.json
#   token = login(data['username'], data['password'])
#   if not token:
#     return jsonify(message='bad username or password given'), 401
#   response = jsonify(access_token=token) 
#   set_access_cookies(response, token)
#   return response

# @auth_views.route('/api/identify', methods=['GET'])
# @jwt_required()
# def identify_user():
#     return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

# @auth_views.route('/api/logout', methods=['GET'])
# def logout_api():
#     response = jsonify(message="Logged Out!")
#     unset_jwt_cookies(response)
#     return response



