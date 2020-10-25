"""

This class is responsible for defining our database.
It is called SQLAlchemy. The bottom line is converted to SQLite.

The benefit of such ORM is that we can easily switch from SQLite to any other SQL (MySQL, PostgreSQL..) by one/two lines of code. 
Because core logic is defined in Python.

@author: JBB Team
"""

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

# JOB table serves both Admin and Users

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.String(100) , nullable=False)
    link = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    approved = db.Column(db.Boolean, unique=False, default=False)
  
    # FOREIGN KEY RELATIONSHIP
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Job('{self.title}', '{self.date_posted}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(9), nullable=False)
    phonenumber = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dob = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    visastatus = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    user_status = db.Column(db.Enum('Regular', 'Exclusive'), default="Regular")
    urole = db.Column(db.String(100), nullable=False, default='User')

    # ONE-TO-MANY RELATIONSHIP WITH JOB (ADMIN)
    job = db.relationship('Job', backref='User', lazy=True)
    
    # ONE-TO-MANY RELATIONSHIP WITH JOB (ADMIN)
    post = db.relationship('Post', backref='User', lazy=True)


    def get_urole(self):
        return urole

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# This serves as a storage for web app's Blog section
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_address = db.Column(db.String(1000), nullable=False)
    hyperlink = db.Column(db.String(1000), nullable=False)
    title = db.Column(db.String(1000), nullable=False)
    content = db.Column(db.String(1000), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer_email = db.Column(db.String(50))
    unix = db.Column(db.Integer)
    payment_date = db.Column(db.String(50))
    username = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    payment_gross = db.Column(db.String(50))
    payment_fee = db.Column(db.String(50))
    payment_net = db.Column(db.String(50))
    payment_status = db.Column(db.String(50))
    tnx_id = db.Column(db.String(50))
    
    def __repr__(self):
        return f"Job('{self.payer_email}', '{self.payment_status}')"

class Favorite(db.Model):
    fav_id = db.Column(db.Integer, primary_key = True)
    job_id = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer)
    
    def __repr__(self):
        return f"Job('{self.job_id}', '{self.user_id}')"