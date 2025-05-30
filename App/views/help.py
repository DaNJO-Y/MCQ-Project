from flask import Flask, Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, unset_jwt_cookies, set_access_cookies, create_access_token, JWTManager
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from App.views.auth import auth_views


from App.controllers import *

help_views = Blueprint('help_views', __name__, template_folder='../templates')

'''
Page/Action Routes
''' 

@help_views.route('/help')
def help_page():
    return render_template('help.html')
