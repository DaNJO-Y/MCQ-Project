from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.controllers import create_user, initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    # initialized will be commented off when in production to prevent loss of data
    # initialize()
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/api_home', methods=['GET'])
def home():
    return '<h1>Info 3604 Project MCQ Bank - MCQ Bank Group</h1>', 200