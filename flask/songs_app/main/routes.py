from flask import Blueprint, render_template, url_for, redirect, flash
from songs_app.models import *
from songs_app.main.forms import *
from songs_app import db

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')


@main.route('/songs/create', methods=['GET', 'POST'])
def create_song():
    form = SongForm()
    if form.validate_on_submit():
        song = Song()
        # TODO: create
        db.session.add(song)
        db.session.commit()
        flash('Song Created.')
        return redirect(url_for('main.show_song', song_id=song.id))
    return render_template('create_song.html', form=form)


@main.route('/songs/<song_id>', methods=['GET'])
def show_song(song_id):
    song = Song.query.get(song_id)
    return render_template('show_song.html', song=song)


@main.route('/songs/<song_id>/edit', methods=['GET', 'POST'])
def edit_song(song_id):
    song = Song.query.get(song_id)
    form = SongForm(obj=song)
    if form.validate_on_submit():
        # TODO: edit
        db.session.add(song)
        db.session.commit()
        flash('Song Edited.')
        return redirect(url_for('main.show_song', song_id=song_id))
    return render_template('edit_song.html', form=form)


@main.route('/songs/<song_id>/delete', methods=['GET', 'POST'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    form = DeleteSongForm()
    # TODO: delete form
    if form.validate_on_submit():
        db.session.delete(song)
        db.session.commit()
        flash('Song Deleted.')
        return redirect(url_for('main.create_song'))
    return render_template('delete_Song.html', form=form)


@main.route('/playlists/create', methods=['GET', 'POST'])
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist = Playlist()
        # TODO: create
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist Created.')
        return redirect(url_for('main.show_playlist', playlist_id=playlist.id))
    return render_template('create_playlist.html', form=form)


@main.route('/playlists/<playlist_id>', methods=['GET'])
def show_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    return render_template('show_playlist.html', playlist=playlist)


@main.route('/playlists/<playlist_id>/edit', methods=['GET', 'POST'])
def edit_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    form = PlaylistForm(obj=playlist)
    if form.validate_on_submit():
        # TODO: edit
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist Edited.')
        return redirect(url_for('main.show_playlist', playlist_id=playlist_id))
    return render_template('edit_playlist.html', form=form)


@main.route('/playlists/<playlist_id>/delete', methods=['GET', 'POST'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    form = DeletePlaylistForm()
    # TODO: delete form
    if form.validate_on_submit():
        db.session.delete(playlist)
        db.session.commit()
        flash('Playlist Deleted.')
        return redirect(url_for('main.create_playlist'))
    return render_template('delete_Playlist.html', form=form)
