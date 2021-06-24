from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm
from .model import Register

class CustomerRegisterForm(FlaskForm):
    name = StringField('')
    username = StringField('', [validators.DataRequired()])
    email = StringField('', [validators.Email(), validators.DataRequired()])
    password = PasswordField('', [validators.DataRequired(), validators.EqualTo('confirm', message='Both password must match!')])
    confirm = PasswordField(' ', [validators.DataRequired()])
    contact = StringField('', [validators.DataRequired()])
    address = StringField('', [validators.DataRequired()])
        
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already in use")
    
    def validate_email(self, email):
        if Register.query.filter_by(email = email.data).first():
            raise ValidationError("This email is already in use")

class CustomerLoginForm(FlaskForm):
    email = StringField('', [validators.Email(), validators.DataRequired()])
    password = PasswordField('', [validators.DataRequired()])
    
    submit = SubmitField('Login')