from songs_app import db


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))

    def __str__(self):
        return f'<Song: {self.title}>'

    def __repr__(self):
        return f'<Song: {self.title}>'


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))

    def __str__(self):
        return f'<Playlist: {self.title}>'

    def __repr__(self):
        return f'<Playlist: {self.title}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))

    def __str__(self):
        return f'<User: {self.username}>'

    def __repr__(self):
        return f'<User: {self.username}>'
