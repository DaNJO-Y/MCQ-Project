from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from.index import index_views

from App.controllers import *

questions_views = Blueprint('questions_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    

@questions_views.route('/myQuestions')
def my_questions_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login'))  # Redirect to login if not logged in

    questions = get_all_my_questions(current_user)  # Fetch only the logged-in teacher's questions
    return render_template('MyQuestions.html', questions=questions)
