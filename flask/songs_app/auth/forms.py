from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, TextAreaField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from songs_app.models import *


class UserForm(FlaskForm):
    username = StringField('User Username')
    password = StringField('User Password')
    submit = SubmitField()
