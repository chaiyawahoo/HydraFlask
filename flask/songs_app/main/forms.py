from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, TextAreaField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from songs_app.models import *


class SongForm(FlaskForm):
    title = StringField('Title')
    artist = StringField('Artist')
    playlist = submit = SubmitField()


class PlaylistForm(FlaskForm):
    title = StringField('Title')
    description = StringField('Description')
    user = song = submit = SubmitField()
