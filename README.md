Steps to execute the wep app - 

1. Open anaconda.exe and navigate to the path where your program lies - do not enter flaskblog folder
2. Execute these commands one by one to import these directories 

* pip install -U Flask-SQLAlchemy
* pip install flask-bcrypt
* pip install flask-login
* pip install flask_user
* pip install Flask-Mail
* pip install email_validator
* pip install Flask-WTF
* pip install flask-admin
* pip install Flask-BasicAuth
* pip install Flask-Session
* pip install requests
* pip install Pillow
* pip install pandas

* set FLASK_APP=flaskblog.py
* set FLASK_ENV=development
* flask run

If you get the following error - sqlalchemy.exc.OperationalError
on command prompt or Anaconda prompt enter following commands - 
1. python 
2. from flaskblog import db
3. db.create_all()


CREDENTIALS:

Admin:
login: admin@jbb.edu
password: abbosali@gwu.edu

Paypal Client:
login: sb-xhisr2638374@personal.example.com
password: DO?tD8h%
* Please let us know if you need any other Paypal details. It's not included here because it includes some personal data
