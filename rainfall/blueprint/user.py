from dataclasses import fields
import logging
import os
from urllib.parse import urljoin

import flask
from google.auth.transport import requests as goog_requests
from google.oauth2 import id_token

from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user
from rainfall.login import check_csrf, save_or_update_google_user
from rainfall.models.user import User


class UserBlueprintFactory:

  def __init__(self, csrf):
    self.csrf = csrf

  def get_blueprint(self):
    user = flask.Blueprint('user', __name__)

    log = logging.getLogger(__name__)

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

    @self.csrf.exempt
    @user.route('/login', methods=['POST'])
    def login():
      resp = check_csrf()
      if resp:
        return resp

      client_id = flask.current_app.config['GOOGLE_CLIENT_ID']
      token = flask.request.form.get('credential')
      try:
        idinfo = id_token.verify_oauth2_token(token, goog_requests.Request(),
                                              client_id)
      except ValueError:
        log.exception('Could not verify token, using: %s', client_id)
        return flask.jsonify(status=400, error='Could not verify token'), 400

      user_id = save_or_update_google_user(idinfo)
      flask.session['user_id'] = user_id
      user = db.session.get(User, user_id)

      frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
      if user.is_welcomed:
        return flask.redirect(urljoin(frontend_url, '/sites'))
      else:
        return flask.redirect(urljoin(frontend_url, '/welcome'))

    @user.route('/user/welcome', methods=['POST'])
    @with_current_user
    def welcome(user):
      user.is_welcomed = True
      db.session.commit()

      return '', 204

    return user
