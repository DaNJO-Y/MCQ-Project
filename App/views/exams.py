from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.views.auth import auth_views

from.index import index_views

from App.controllers import *

exams_views = Blueprint('exams_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    

@exams_views.route('/myExams')
def my_exams_page():
    if not current_user.is_authenticated:
        return redirect(url_for('auth_views.login'))  # Redirect to login if not logged in

    #exams = get_exams(current_user,page=1, per_page=10)  # Fetch only the logged-in teacher's questions
    #return render_template('MyExams.html', exams=exams)
    response = get_exams(current_user, page=1, per_page=10)
    if isinstance(response, tuple):  # Handling error responses
        response, status = response
        if status == 404:
            flash("No exams found", "warning")
            response["exams"] = []

    return render_template('MyExams.html', exams=response["exams"])

