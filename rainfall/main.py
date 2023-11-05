from dataclasses import fields
from functools import wraps
import os
import time
from urllib.parse import urljoin

from google.oauth2 import id_token
from google.auth.transport import requests as goog_requests
import flask

from rainfall.db import db
from rainfall.login import check_csrf, save_or_update_google_user
from rainfall.models.site import Site
from rainfall.models.user import User


def with_current_user(f):

  @wraps(f)
  def wrapped(*args, **kwargs):
    user_id = flask.session.get('user_id')
    if user_id is None:
      return flask.jsonify(status=404, error='No signed in user'), 404

    user = db.session.get(User, user_id)
    if user is None:
      return flask.jsonify(status=404, error='No signed in user'), 404

    value = f(*args, user, **kwargs)
    return value

  return wrapped


def create_app():
  app = flask.Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
  app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
  if os.environ.get('RAINFALL_ENV') != 'test':
    db.init_app(app)

  GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
  RAINFALL_FRONTEND_URL = os.environ['RAINFALL_FRONTEND_URL']

  @app.route('/')
  def index():
    return 'Hello flask'

  @app.route('/api/v1/user')
  @with_current_user
  def get_user(user):
    user_without_sites = dict((field.name, getattr(user, field.name))
                              for field in fields(user)
                              if field.name != 'sites')
    return flask.jsonify(user_without_sites)

  @app.route('/api/v1/logout')
  def logout():
    if 'user_id' in flask.session:
      del flask.session['user_id']
    return '', 204

  @app.route('/api/v1/login', methods=['POST'])
  def login():
    resp = check_csrf()
    if resp:
      return resp

    token = flask.request.form.get('credential')
    try:
      idinfo = id_token.verify_oauth2_token(token, goog_requests.Request(),
                                            GOOGLE_CLIENT_ID)
    except ValueError:
      return flask.jsonify(status=400, error='Could not verify token'), 400

    user_id = save_or_update_google_user(idinfo)
    flask.session['user_id'] = user_id
    user = db.session.get(User, user_id)

    if user.is_welcomed:
      return flask.redirect(urljoin(RAINFALL_FRONTEND_URL, '/sites'))
    else:
      return flask.redirect(urljoin(RAINFALL_FRONTEND_URL, '/welcome'))

  @app.route('/api/v1/user/welcome', methods=['POST'])
  @with_current_user
  def welcome(user):
    user.is_welcomed = True
    db.session.commit()

    return '', 204

  @app.route('/api/v1/site', methods=['POST'])
  @with_current_user
  def create_site(user):
    if not user.is_welcomed:
      return flask.jsonify(status=400,
                           error='User has not yet been welcomed'), 400

    data = flask.request.get_json()
    if data is None:
      return flask.jsonify(status=400, error='No JSON provided'), 400
    site_data = data.get('site')
    if site_data is None:
      return flask.jsonify(status=400, error='Missing site data'), 400
    if site_data.get('name') is None:
      return flask.jsonify(status=400, error='Site name is required'), 400

    user.sites.append(Site(**site_data))
    db.session.add(user)
    db.session.commit()

    return '', 204

  return app
