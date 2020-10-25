'''
This class is responsible for connecting web pages (.html files) to the database through the use of Python.
Here we also handle WSGI requests and deliver appropriate response.

@author: JBB Team
'''
# MAIN IMPORTS (BOTH INTERNAL AND EXTERNAL)
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail 
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             RequestResetForm, ResetPasswordForm, GitHubPost, MusePost, JobSearchForm)
from flaskblog.models import User, Post, Job, Payment, Favorite
from flask_login import login_user, current_user, logout_user, login_required
import flask_login
from flask_mail import Message

# IMPORTS FOR ADMIN SECTION
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flaskblog import gitrequest, muserequest
from datetime import datetime
from functools import wraps

# IMPORTS FOR PAYMENT SECTION
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests
import time

# Class variable for holding session values
session_variable = dict()

# Re-defining login logic so that we differentiate between User and Admin access
def login_required(role="Admin"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # in case if user is not authenticated
            if not current_user.is_authenticated:
               return app.login_manager.unauthorized()
           # Getting role value from the database
           # Conditional: 
            if current_user.urole != role:
                if current_user.urole == 'User':
                    return app.login_manager.unauthorized() 
                else:
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('admin.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/analysis")
@login_required('User')
def analysis():
    return render_template('analysis.html', title='Analysis')

@app.route("/savedjobs", methods=['GET', 'POST'])
@login_required('User')
def saved_jobs():
    user = flask_login.current_user
    subquery = db.session.query(Favorite.job_id).filter(Favorite.user_id == user.id)
    jobs = Job.query.filter(Job.id.in_(subquery))
    if request.method == "GET" and request.query_string:
        # delete job_id from favorite table
        jobId = request.args.get('jobId')
        favorite = Favorite.query.filter(
            Favorite.job_id == jobId, 
            Favorite.user_id == user.id).first()
        db.session.delete(favorite)
        db.session.commit()

        # Moving saved elements away from jobs view
        subquery = db.session.query(Favorite.job_id).filter(Favorite.user_id == user.id)
        query = Job.query.filter(Job.id.in_(subquery))
        return render_template('savedjobs.html', jobs = query)
    return render_template('savedjobs.html', jobs=jobs)

@app.route("/jobs", methods=['GET', 'POST'])
@login_required('User')
def jobs():
    search_form = JobSearchForm()
    user = flask_login.current_user

    if request.method == "POST":
        title = search_form.title.data
        description = search_form.description.data
        company_name= search_form.company_name.data

        if title and description and company_name: 
            jobs = Job.query.filter(
                Job.title.like(f"%{title}%"),
                Job.description.like(f"%{description}%"),
                Job.company_name.like(f"%{company_name}%"))
        elif title and description and not company_name:
            jobs = Job.query.filter(
                Job.title.like(f"%{title}%"),
                Job.description.like(f"%{description}%")
                )
        elif title and company_name and not description:
            jobs = Job.query.filter(
                Job.title.like(f"%{title}%"),
                Job.company_name.like(f"%{company_name}%")
                )
        elif description and company_name and not title:
            jobs = Job.query.filter(
                Job.description.like(f"%{description}%"),
                Job.company_name.like(f"%{company_name}%")
                )
        elif title and not description and not company_name:
            jobs = Job.query.filter(Job.title.like(f"%{title}%"))
        elif description and not title and not company_name:
            jobs = Job.query.filter(Job.description.like(f"%{description}%"))
        else:
            jobs = Job.query.filter(Job.company_name.like(f"%{company_name}%"))

        return render_template('jobs.html', jobs=jobs, form=search_form)

    elif request.method == "GET" and request.query_string:
        # Saving favorite jobs to database
        user = flask_login.current_user
        jobId = request.args.get('jobId')
        favorite = Favorite(job_id = jobId, user_id = user.id)
        db.session.add(favorite)
        db.session.commit()
        
        # Moving saved elements away from jobs view
        subquery = db.session.query(Favorite.job_id).filter(Favorite.user_id == user.id)
        query = Job.query.filter(~Job.id.in_(subquery))
        return render_template('jobs.html', jobs = query, form = search_form)

    subquery = db.session.query(Favorite.job_id).filter(Favorite.user_id == user.id)
    jobs = Job.query.filter(~Job.id.in_(subquery))
    return render_template('jobs.html', jobs=jobs, form=search_form)

@app.route("/blogs")
@login_required('User')
def blogs():
    posts = Post.query.order_by(Post.title.desc())
    return render_template('blogs.html', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # IF user is not authenticated -> POST
    form = RegistrationForm()

    # if method is POST 
    if form.validate_on_submit():
        if 'edu' not in form.email.data:
            flash('Only .edu emails are accepted', 'error')
            redirect(url_for('register'))
        else:
            # Hashing password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # Storing user data on User db Object
            user = User(firstname = form.firstname.data, lastname = form.lastname.data, 
                        street = form.street.data, city = form.city.data, zipcode = form.zipcode.data, 
                        phonenumber = form.phonenumber.data, email = form.email.data, 
                        dob = form.dob.data, gender = form.gender.data,
                        visastatus = form.visastatus.data, username=form.username.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            session_variable['username'] = user.username
            # Flashing a message
            flash('Your account has been created! Proceeding to payment', 'success')
            return redirect(url_for('purchase', name = user.firstname))
    # if the form is empty, we return register.html with Registration Form
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # session check: if user is authenticated
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # in case if not authenticated then LoginForm is created
    form = LoginForm()
    # checking if it is a POST request and if it is valid
    if form.validate_on_submit():
        # Getting user based on form's email
        user = User.query.filter_by(email=form.email.data).first()
        # checking if there is an object user and if db's user password matches form's password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # page name if the user successfully logged in
            next_page = request.url_rule
            if user.urole == 'Admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.index'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('login'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    # if the form is empty and user is not authenticated then we render a login html with login form
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required('User')
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='kswarchaa@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

### ADMIN SECTION

# User Model
class MyUserView(ModelView):

    page_size = 50 
    column_exclude_list = ['password', ]
    can_create = False
    column_searchable_list = ['username']
    column_filters = ['username']
    column_editable_list = ['username', 'email']
    can_export = True

    def is_accessible(self):
        return True
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    def _handle_view(self, name, export_type = 'CSV'):
        if not self.is_accessible():
            return redirect(url_for('login'))

# Post Model
class MyPostView(ModelView):

    page_size = 50 
    column_exclude_list = ['password', ]
    column_searchable_list = ['title', 'image_address']
    column_filters = ['title', 'image_address']
    column_editable_list = ['title', 'image_address','hyperlink']
    can_export = True

    def is_accessible(self):
        return True
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    def _handle_view(self, name, export_type = 'CSV'):
        if not self.is_accessible():
            return redirect(url_for('login'))

# Job Model
class MyJobView(ModelView):
    
    page_size = 2
    column_searchable_list = ['title', 'description', 'company_name', 'date_posted', 'link']
    column_filters = ['title', 'description', 'company_name']
    column_editable_list = ['title', 'description', 'company_name', 'date_posted', 'link']
    can_export = True
    
    def is_accessible(self):
        return True
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    def _handle_view(self, name, export_type = 'CSV'):
        if not self.is_accessible():
            return redirect(url_for('login'))

class MyGithubView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        # Get data from the form
        form = GitHubPost()
        if request.method == 'POST':
            # GET DATA FROM FORM
            # SEND IT TO GITREQUEST CLASS
            git = gitrequest.GitRequest(form.description.data, form.location.data, form.fulltime.data)
            git_link = git.create_link()
            response = git.make_request(git_link)
            
            # GET RESULTS FROM GITREQUEST
            response_table = git.get_table(response)
            # STORE IT TO DB
            for i in range(len(response_table['title'])):
                j = Job(title = response_table.iloc[i,0],
                        description = response_table.iloc[i,1],
                        company_name = response_table.iloc[i,2],
                        date_posted = response_table.iloc[i,3],
                        link = response_table.iloc[i,4],
                        source = response_table.iloc[i,5])
                db.session.add(j)
                db.session.commit()
            return redirect(url_for('job.index_view'))
        return self.render('admin/github.html', form=form)

class MyMuseView(BaseView):
    @expose('/', methods=('GET','POST'))
    def muse(self):
        form = MusePost()
        if request.method == 'POST':
            # GET DATA FROM FORM
            # SEND IT TO MUSEREQUEST CLASS
            muse = muserequest.MuseRequest(position_name = form.position_name.data,
                                           category = form.category.data,
                                           page = form.page.data,
                                           level = form.level.data)
            link = muse.create_link()
            
            # GET RESULTS FROM MUSEREQUEST
            response = muse.make_request(link)
            response_table = muse.get_jobs(response)
            user = User.query.filter_by(urole='Admin').first()

            # STORE IT TO DB
            for i in range(len(response_table['title'])):
                j = Job(title = response_table.iloc[i,0],
                        description = response_table.iloc[i,1],
                        company_name = response_table.iloc[i,2],
                        date_posted = response_table.iloc[i,3],
                        link = response_table.iloc[i,4],
                        source = response_table.iloc[i,5],
                        admin_id = user.id)
                db.session.add(j)
                db.session.commit()
            return redirect(url_for('job.index_view'))
        return self.render('admin/muse.html', form=form)


# Main Admin Page
class MyAdminIndexView(AdminIndexView):
    
    def is_acessible(self):
        return True

    @login_required('Admin')
    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('login'))
        else:
            return self.render('admin/index.html')

# Admin Logout
class LogoutMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.is_authenticated  

# Instantiation of two windows related to admin
admin = Admin(app, name = 'Admin: Jobs Beyond Border',index_view = MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(MyUserView(User, db.session, category="Manage")) 
admin.add_view(MyPostView(Post, db.session, category="Manage"))
admin.add_view(MyGithubView(category="APIs"))
admin.add_view(MyMuseView(category="APIs"))
admin.add_view(MyJobView(Job, db.session))
admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))

### PAYMENT SECTION
@app.route('/ipn/', methods = ['POST'])
def ipn():
    try:
        arg = ''
        request.parameter_storage_class = ImmutableOrderedMultiDict
        values = request.form

        for x,y in values.iteritems():
            arg += "&{x}={y}".format(x=x,y=y)

        validate_url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_notify-validate{arg}".format(arg=arg)

        r = request.get(validate_url)
        if r.text == "VERIFIED":
            try:
                payer_email = request.form.get('payer_email')
                unix = int(time.time())
                payment_date = request.form.get('payment_date')
                username = request.form.get('custom')
                last_name = request.form.get('last_name')
                payment_gross = request.form.get('payment_gross')
                payment_fee = request.form.get('payment_fee')
                payment_net = float(payment_gross) - float(payment_fee)
                payment_status = request.form.get('payment_status')
                tnx_id = request.form.get('tnx.id')

            except Exception as e:

                with open('tmp/ipnout.txt', 'a') as f:
                    data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
                    f.write(data)
                    print("ERROR")

            with open('tmp/inpout.txt', 'a') as f:
                data = 'SUCCESS\n'+str(values)+'\n'
                f.write(data)
                print("SUCCESS")

            statement = Payment(payer_email = payer_email, 
                                unix = unix, 
                                payment_date = payment_date, 
                                username = username, 
                                last_name = last_name, 
                                payment_gross = payment_gross, 
                                payment_fee = payment_fee, 
                                payment_net = payment_net, 
                                payment_status = payment_status,
                                tnx_id = tnx_id)
            db.session.add(statement)
            db.session.commit()

            # STORING DATA IN THE DATABASE PART
        else:
            with open('tmp/ipnout.txt', 'a') as f:
                data = 'FAILURE\n'+str(values)+'\n'
                f.write(data)
                print("FAILURE")
        return r.text
    except Exception as e:
        return str(e)

@app.route('/success/')
def success():
    try:
        usr_name = session_variable.get('username', None)
        user = User.query.filter_by(username=usr_name).first()
        user.user_status = "Exclusive"
        db.session.commit()
        return render_template("success.html")
    except Exception as e:
        return(str(e))

@app.route('/purchase/')
def purchase():
    try:
        ref = request.args.get('name', None)
        return render_template('subscribe.html', referrer=ref)
    except Exception as e:
        return str(e)