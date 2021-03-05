from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField, TextAreaField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from songs_app.models import *


class SongForm(FlaskForm):
    title = StringField('Song Title')
    artist = StringField('Song Artist')
    submit = SubmitField()


class PlaylistForm(FlaskForm):
    title = StringField('Playlist Title')
    description = StringField('Playlist Description')
    submit = SubmitField()
