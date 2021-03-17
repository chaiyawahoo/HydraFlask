from songs_app import db


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    playlists = db.relationship(
        'Playlist', secondary='playlists_songs', back_populates='songs')

    def __str__(self):
        return f'<Song: {self.title}>'

    def __repr__(self):
        return f'<Song: {self.title}>'


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    user = db.relationship('User', back_populates='playlists')
    songs = db.relationship(
        'Song', secondary='playlists_songs', back_populates='playlists')

    def __str__(self):
        return f'<Playlist: {self.title}>'

    def __repr__(self):
        return f'<Playlist: {self.title}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200))
    dt = db.Column(db.DateTime)
    playlists = db.relationship('Playlist', back_populates='user')

    def __str__(self):
        return f'<User: {self.username}>'

    def __repr__(self):
        return f'<User: {self.username}>'


playlists_songs = db.Table('playlists_songs', db.Column('playlist_id', db.Integer, db.ForeignKey(
    'playlist.id')),  db.Column('song_id', db.Integer, db.ForeignKey('song.id')))
