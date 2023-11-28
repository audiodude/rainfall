from dataclasses import fields
import os
from urllib.parse import urljoin

import flask
from google.auth.transport import requests as goog_requests
from google.oauth2 import id_token

from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user
from rainfall.login import check_csrf, save_or_update_google_user
from rainfall.models.user import User

user = flask.Blueprint('user', __name__)

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
RAINFALL_FRONTEND_URL = os.environ['RAINFALL_FRONTEND_URL']


@user.route('/user')
@with_current_user
def get_user(user):
  user_without_sites = dict((field.name, getattr(user, field.name))
                            for field in fields(user)
                            if field.name != 'sites')
  return flask.jsonify(user_without_sites)


@user.route('/logout')
def logout():
  if 'user_id' in flask.session:
    del flask.session['user_id']
  return '', 204


@user.route('/login', methods=['POST'])
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


@user.route('/user/welcome', methods=['POST'])
@with_current_user
def welcome(user):
  user.is_welcomed = True
  db.session.commit()

  return '', 204
