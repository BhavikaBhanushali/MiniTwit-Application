# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging REST API written with Flask and sqlite3.

"""

import time
import click
from flask_basicauth import BasicAuth
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, jsonify, request, session, url_for, redirect, make_response, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash



# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('mt_api')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_user_details():
    """Convenience method to look up the user."""
    rv = query_db('select * from user')
    return rv[0] if rv else None


class MyBasicAuth(BasicAuth):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def check_credentials(self, username, password):
        if username != None and password != None:

            user_profile = query_db('select * from user where username = ?',[username], one=True)
            if user_profile != None:
                if user_profile['username'] == username:
                    if check_password_hash(user_profile['pw_hash'], password):
                        return 'true'
                else:
                        return None
            else:
                return None
        else:
            return None

basic_auth = MyBasicAuth(app)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context."""
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def populate_db():
    db = get_db()
    with app.open_resource('population.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('populatedb')
def populatedb_command():
    """Populates tables."""
    populate_db()
    print('populated the database.')

####### Database setup completes #######


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

#API to fetch user ID
@app.route('/api/userid/<username>', methods=['GET'])
def get_user(username):
    user_id = get_user_id(username)

    return jsonify({'user_id': user_id}), 200


#API to fetch user information
@app.route('/api/u_info/<user_id>', methods=['GET'])
def user_info(user_id):
    user = query_db('select * from user where user_id = ?',
                          [user_id], one=True)
    if user is None:
        abort(404)
    else:
        user_info = {"user_id": user['user_id'],"username":user['username'],"email":user['email']}
        return jsonify({'user_info': user_info}), 200

#API for user home page
@app.route('/api/homepage', methods=['GET'])
@basic_auth.required
def users_being_followed_tweets():
    """Displays a tweets of user being followed."""
    username = request.authorization.username
    tweets = []

    user_id = get_user_id(username);
    tuples = query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''',
        [user_id, user_id, PER_PAGE])

    for tuple in tuples:
        tweet = {}
        tweet["message_id"] = tuple['message_id']
        tweet["author_id"] = tuple['author_id']
        tweet["text"] = tuple['text']
        tweet["pub_date"] = tuple['pub_date']
        tweet["username"] = tuple['username']
        tweet["email"] = tuple['email']
        tweets.append(tweet)

    return jsonify({'tweets': tweets}), 200

#API for User Registration which allows new user to register #
@app.route('/api/user', methods=['POST'])
def register():
    if request.method == 'POST':

       if not request.json:
        return jsonify({'message':'Bad request'}),400
    else:
        db = get_db()
        db.execute('''insert into user (
              username, email, pw_hash) values (?, ?, ?)''',
              [request.json.get('username'), request.json.get('email'),
               generate_password_hash(request.json.get('password'))])
        db.commit()
        flash('New User Registration succesfully completed and you can login now')
    return jsonify({'message': 'User successfully registered'}), 201

# User Login API which allows user to login with valid credentials#
@app.route('/api/login', methods=['POST'])
def user_login():
    """Allows user to login with valid credentials"""
    user = query_db('''select * from user where username = ?''', [request.authorization.username], one=True)
    if user is None:
        error = 'Invalid username'
    elif not check_password_hash(user['pw_hash'],request.authorization.password):
        error = 'Invalid password'
    else:
        flash('You were logged in')
    return jsonify({'user_id':user['user_id']}),200

# Add the new tweet into the database #
@app.route('/api/tweet', methods=['POST'])
@basic_auth.required
def add_tweet():
    """Add a new tweet from the user."""
    if not request.json or 'author_id' not in request.json or 'text' not in request.json:
        abort(400)

    db = get_db()

    author_id = request.json.get('author_id')
    text = request.json.get('text')
    pub_date = int(time.time())

    db.execute('''insert into message (author_id, text, pub_date) values (?, ?, ?)''', (author_id, text, pub_date))
    db.commit()
    flash('Message recorded succesfully')
    message = {"author_id": author_id, "text": text, "pub_date": pub_date}
    return jsonify({'message': message}), 201

# Displays all the tweets irrespective of the user
@app.route('/api/publictimeline', methods=['GET'])
#@basic_auth.required
def list_tweets():
    """Displays all the tweets on publictimeline."""
    tweets = []
    tuples = query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE])
    for tuple in tuples:
        tweet = {}
        tweet["username"] = tuple['username']
        tweet["email"] = tuple['email']
        tweet["text"] = tuple['text']
        tweet["pub_date"] = tuple['pub_date']
        tweets.append(tweet)
    return jsonify({'tweets':tweets}),200

# Displays all the tweets of the particular user
@app.route('/api/usertimeline/<username>', methods=['POST'])
def list_user_tweets(username):
    """Displays a users tweets."""
    userdata = query_db('select * from user where username = ?',
    [username], one=True)
    if userdata is None:
        abort(404)
    else:
        user_details = {"username": userdata['username'],"user_id":userdata['user_id']}

        followed = False
    if request.json.get('user_id') is not None:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [request.json.get('user_id'), user_details.get('user_id')],
            one=True) is not None

    user_tweets = []
    if user_details is None:
        return jsonify({'message': 'User not found'}), 404
    tuples = query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [user_details['user_id'], PER_PAGE])

    for tuple in tuples:
            user_tweet = {}
            user_tweet["username"] = tuple['username']
            user_tweet["email"] = tuple['email']
            user_tweet["text"] = tuple['text']
            user_tweet["pub_date"] = tuple['pub_date']
            user_tweets.append(user_tweet)

    return jsonify({'user_tweets':user_tweets, 'followed' : followed, 'user_details':user_details}),200


# Displays all the tweets from the user being followed
@app.route('/api/home/<username>', methods=['GET'])
@basic_auth.required
def tweets_following_users(username):
    """Displays a tweets of user being followed."""
    user_profile = query_db('select * from user where username = ?',
                            [username], one=True)
    follow_tweets = []

    if user_profile is None:
        abort(404)

    tuples = query_db('''select message.* from message, follower where
                           follower.whom_id = message.author_id and follower.who_id = ?
                           order by message.pub_date desc limit ?''', [user_profile['user_id'], PER_PAGE])

    for tuple in tuples:
        follow_tweet = {}
        follow_tweet["message_id"] = tuple['message_id']
        follow_tweet["author_id"] = tuple['author_id']
        follow_tweet["text"] = tuple['text']
        follow_tweet["pub_date"] = tuple['pub_date']
        follow_tweets.append(follow_tweet)

    return jsonify({'follow_tweets': follow_tweets}), 200

# API for Follow User#
@app.route('/api/<whomUserName>/follower/<whoUserName>', methods=['POST'])
@basic_auth.required
def follow(whomUserName,whoUserName):
    """Adds the current user as follower of the given user."""

    whomuser = query_db('select * from user where username = ?',
                            [whomUserName], one=True)
    whouser = query_db('select * from user where username = ?',
                            [whoUserName], one=True)


    followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [whouser['user_id'], whomuser['user_id']],one=True) is not None

    if whouser is None:
        return jsonify({'message':'User trying to follow another user which does not exist'}),404

    if whomuser is None:
        return jsonify({'message':'User getting followed does not exist yet'}),404

    if not followed:
        db = get_db()

        db.execute('''insert into follower (
              who_id, whom_id) values (?, ?)''',
              [whouser['user_id'], whomuser['user_id']])
        db.commit()
        flash('Operation successful')
        return jsonify({'message': 'Successfully following'}), 201
    else:
        return jsonify({'message':'Specified user is already following another user'}),403

# API for Unfollow the user#
@app.route('/api/<whomUserName>/follower/<whoUserName>', methods=['DELETE'])
@basic_auth.required
def unfollow(whomUserName,whoUserName):
    """Unfollows the user"""

    whomuser = query_db('select * from user where username = ?',
                            [whomUserName], one=True)
    whouser = query_db('select * from user where username = ?',
                            [whoUserName], one=True)
    followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [whouser['user_id'], whomuser['user_id']],one=True) is not None

    if whouser is None:
        return jsonify({'message':'User trying to unfollow another user does not exist'}),404

    if whomuser is None:
        return jsonify({'message':'User getting unfollowed does not exist yet'}),404

    if followed:
        db = get_db()

        db.execute('delete from follower where who_id=? and whom_id=?',
              [whouser['user_id'], whomuser['user_id']])
        print("Delete Success")
        db.commit()
        flash('Operation successful')
        return jsonify({'message': 'User Successfully unfollowing the specified user'}), 201
    else:
        return jsonify({'message':'Specified user is not following another user'}),404
