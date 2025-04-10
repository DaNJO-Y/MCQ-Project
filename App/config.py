import os
# from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv



load_dotenv()
def load_config(app, overrides):
    if os.path.exists(os.path.join('./App', 'custom_config.py')):
        app.config.from_object('App.custom_config')
    else:
        app.config.from_object('App.default_config')
    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
    # app.config['SENDGRID_API_KEY'] = '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'
    app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')
    app.config['MAIL_SERVER']= 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    # app.config['MAIL_USERNAME'] = 'd4884781@gmail.com'  # Replace with your Gmail address
    # app.config['MAIL_PASSWORD'] = 'hxny nokz pgjr txrq'      # Replace with your Gmail password or App Password
    app.config['MAIL_DEFAULT_SENDER'] = 'd4884781@gmail.com'
    # app.config['SECRET_KEY'] = 'c?|CVNoxkYqfB}|o$A6G'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    mail = Mail(app)
   
    for key in overrides:
        app.config[key] = overrides[key]


