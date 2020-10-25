'''

This class is responsible for having flaskblog file as a Module so that 
import statements become available.

Also it incorporates security features and some other low-level configrations of the web application.

'''

import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_basicauth import BasicAuth 

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# LOGIN MANAGER
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jobsbeyondborder@gmail.com'
app.config['MAIL_PASSWORD'] = 'msistcapstone'
mail = Mail(app)

# ADMIN SIDE
app.config['FLASK_ADMIN_SWATCH'] = 'Paper' # Admin theme

# for some reason import should be on the last line
from flaskblog import routes
