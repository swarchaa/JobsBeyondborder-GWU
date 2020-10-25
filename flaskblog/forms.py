'''

This class is responsible for defining web application forms (<form>).
It is defined as a Python class that extends FlaskForm that includes security patches necessary to protect forms from various cyber attacks.
These forms are then passed to .html files through routes.py

'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField, IntegerField, SelectField
from wtforms.fields.html5 import DateField, TelField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, NumberRange
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',
                        validators=[DataRequired()])
    lastname = StringField('Last Name',
                        validators=[DataRequired()])
    street= StringField('Street Address',
                        validators=[DataRequired()])
    city = StringField('City',
                        validators=[DataRequired()])
    zipcode= IntegerField('Zip Code',
                        validators=[DataRequired(), 
                                    NumberRange(min=11111, max=99999, message="Please include a valid ZipCode")],
                        render_kw={"placeholder": "00000"})
    phonenumber = IntegerField('Phone Number', validators=[DataRequired(), 
                                                           NumberRange(min=1111111111, max=9999999999, message="Please include a valid Phone Number")],
                               render_kw={"placeholder": "(111) 111-1111"})
    email = StringField('Email',
                        validators=[DataRequired(), Email()], render_kw={"placeholder": ".edu"})
    dob = DateField('Date of Birth',
                        validators=[DataRequired()])

    gender= SelectField('Gender',validators=[DataRequired()],
                        choices=[('Male', 'Male'),
                                 ('Female', 'Female'),
                                 ('Undecided', 'Undecided')])

    visastatus = SelectField('Visa Status', [DataRequired()],
                        choices=[('F-1', 'F-1'),
                                 ('J-1', 'J-1')])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=12), 
                                                      Regexp('^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])',0, "There should be at least one Upper case, one Lower case, one number and one special character") ])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register & Proceed to Payment')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class JobSearchForm(FlaskForm):
    title = StringField('Job Title')
    description = StringField('Description')
    company_name=StringField('Company Name')
    submit = SubmitField('Search')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
"""
# MODEL POST WAS CHANGED; PLEASE REFLECT THE CHANGE HERE
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
"""

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

### ADMIN SECTION
class GitHubPost(FlaskForm):
    description = StringField('Job Description',
                              validators=[DataRequired()])
    location = StringField('City in the US',
                           validators=[DataRequired()])
    fulltime = RadioField('Full-time', choices=[(1, 'Yes'),(0, 'No')])
    submit = SubmitField('Get Jobs')

class MusePost(FlaskForm):
    position_name = StringField('Name of Position',
                              validators=[DataRequired()])

    category_accepted_values = ["Account Management", "Creative & Design", "Data Science", "Education",
        "Finance", "Healthcare & Medicine", "Legal","Operations", "Retail","Social Media & Community",
        "Business & Strategy","Customer Service","Editorial","Engineering","Fundraising & Development","HR & Recruiting",
        "Marketing & PR", "Project & Product Management", "Sales"]
    category = SelectField(u"Job Category", choices = category_accepted_values, validators = [DataRequired()])

    page = IntegerField('The page number to load', validators=[DataRequired()])

    level_accepted_values = ["Entry level", "Senior level", "Mid level", "Internship", "management"]
    level = SelectField(u"Level of Experience", choices = level_accepted_values, validators = [DataRequired()])

    submit = SubmitField('Get Jobs')