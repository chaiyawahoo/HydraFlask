from flask import Blueprint, render_template, url_for, redirect, flash
from songs_app.models import *
from songs_app.auth.forms import *
from songs_app import db

auth = Blueprint('auth', __name__)


@auth.route('/users/create', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        # TODO: create
        db.session.add(user)
        db.session.commit()
        flash('User Created.')
        return redirect(url_for('auth.show_user', user_id=user.id))
    return render_template('create_user.html', form=form)


@auth.route('/users/<user_id>', methods=['GET'])
def show_user(user_id):
    user = User.query.get(user_id)
    return render_template('show_user.html', user=user)


@auth.route('/users/<user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        # TODO: edit
        db.session.add(user)
        db.session.commit()
        flash('User Edited.')
        return redirect(url_for('auth.show_user', user_id=user_id))
    return render_template('edit_user.html', form=form)


@auth.route('/users/<user_id>/delete', methods=['GET', 'POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    form = DeleteUserForm()
    # TODO: delete form
    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        flash('User Deleted.')
        return redirect(url_for('auth.create_user'))
    return render_template('delete_User.html', form=form)
