# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: © 2010 by the Pallets team.
    :license: BSD, see LICENSE for more details.
"""

import time
import base64
import requests
import json
from json import dumps
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash


# configuration
API_BASE_URL = 'http://localhost:8080'
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    response = requests.get(API_BASE_URL + '/api/userid/' + username)
    server_response = json.loads(response.text)

    if response.status_code == requests.codes.unauthorized:
        print server_response.get('error')
        return None
    else:
        return server_response.get('user_id')

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        response = requests.get(API_BASE_URL + '/api/u_info/' + str(session['user_id']))
        user_info = json.loads(response.text)
        g.user = user_info.get('user_info',[])

@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    response = requests.get(API_BASE_URL + '/api/homepage', auth=(session['username'], session['password']))

    all_messages = json.loads(response.text)
    return render_template('timeline.html', messages = all_messages.get('tweets', []))


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    response = requests.get(API_BASE_URL + '/api/publictimeline')

    #JSON-encoded string into a Python dictionary data structure
    all_messages = json.loads(response.text)
    return render_template('timeline.html', messages = all_messages.get('tweets', []))

@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""

    payload = {}

    if g.user:
        payload = {'user_id': session['user_id']}

    response = requests.post(API_BASE_URL + '/api/usertimeline/' + username, json=payload)
    timeline_details = json.loads(response.text)
    user_details = timeline_details.get('user_details')
    if user_details is None:
        abort(404)

    return render_template('timeline.html', messages = timeline_details.get('user_tweets'), followed = timeline_details.get('followed'),
            profile_user = user_details)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    response = requests.post(API_BASE_URL + '/api/' + username + '/follower/' + session['username'], auth=(session['username'], session['password']))
    if response.status_code == requests.codes.created:
        flash('You are now following "%s"' % username)
        return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    response = requests.delete(API_BASE_URL + '/api/' + username + '/follower/' +  session['username'], auth=(session['username'], session['password']))
    if response.status_code == requests.codes.created:
        flash('You are no longer following "%s"' % username)
        return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        payload = {'author_id': session['user_id'], 'text': request.form['text']}
        response = requests.post(API_BASE_URL + '/api/tweet', auth=(session['username'], session['password']), json=payload)

    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None

    if request.method == 'POST':
        payload = {'username': request.form['username'], 'password': request.form['password']}
        response = requests.post(API_BASE_URL + '/api/login', auth =(request.form['username'], request.form['password']))
        server_response = json.loads(response.text)

        if response.status_code == requests.codes.unauthorized:
            error = server_response.get('error')
        else:
            flash('You were logged in')
            session['user_id'] = server_response.get('user_id')
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            payload = {'username': request.form['username'], 'password': request.form['password'], 'email':request.form['email']}
            response = requests.post(API_BASE_URL + '/api/user', json=payload)

            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
