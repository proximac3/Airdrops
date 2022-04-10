from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField, validators
from wtforms.validators import InputRequired, Optional, Email

#signup form
class SignupForm(FlaskForm):
    """Form for signing up new user"""
    
    username = StringField('Username', render_kw={"placeholder": "Enter Username"},
                           validators=[InputRequired(message="Username Required")])
    email = StringField('Email', render_kw={"placeholder": "Enter Email"}, 
                        validators=[InputRequired(message="Password Required")])
    password = PasswordField('Password', render_kw={"placeholder": "Create New Password"}, 
                             validators=[InputRequired(message="Password Required")])


class LoginForm(FlaskForm):
    """Login Form"""
    
    username = StringField('Username', render_kw={"placeholder": "Enter Username"}, 
                           validators=[InputRequired(message="Username Required")])
    password = PasswordField('Password', render_kw={"placeholder": "Enter Password"}, 
                             validators=[InputRequired(message="Password Required")])

class UpdateEmployeeForm(FlaskForm):
    """Update Employee details"""
    username = StringField('Username', render_kw={"placeholder": "Enter Username"},
                           validators=[InputRequired(message="Username Required")])
    email = StringField('Email', render_kw={"placeholder": "Enter Email"}, 
                        validators=[InputRequired(message="Password Required")])


