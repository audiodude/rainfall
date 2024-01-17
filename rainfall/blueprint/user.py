from dataclasses import fields
import logging
import os
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

import flask
from google.auth.transport import requests as goog_requests
from google.oauth2 import id_token
from sqlalchemy import select

from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user
from rainfall.login import check_csrf, save_or_update_google_user, register_mastodon_app, redirect_to_instance
from rainfall.models.mastodon_credential import MastodonCredential
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

    @user.route('/logout', methods=['POST'])
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

    @user.route('/mastodon/init', methods=['POST'])
    def mastodon_init():
      host = flask.request.form.get('host')
      if host is None:
        # TODO: Figure out a way to load the MastodonLoginView with an error message.
        return flask.jsonify(status=400,
                             error='The field `host` is required'), 400

      if not host.startswith('https://'):
        host = 'https://' + host
      parsed = urlparse(host)
      netloc = parsed.netloc

      stmt = select(MastodonCredential).where(
          MastodonCredential.netloc == netloc)
      result = db.session.execute(stmt)
      creds = result.fetchone()

      # We have not yet registered an app with this server.
      if creds is None:
        creds = register_mastodon_app(netloc)
      else:
        creds = creds[0]

      if creds is None:
        # TODO: Figure out a way to load the MastodonLoginView with an error message.
        return flask.jsonify(status=400,
                             error='Could not find that Mastodon host'), 400

      return redirect_to_instance(creds)

    @self.csrf.exempt
    @user.route('/mastodon/login')
    def mastodon_login():
      code = flask.request.args.get('code')
      if not code:
        # TODO: Do something
        pass

      # TODO: Make a request to the home server and verify the login, then create a User object
      # and redirect to the welcome or sites page.
      return flask.redirect(flask.current_app.config['RAINFALL_FRONTEND_URL'])

    @user.route('/user/welcome', methods=['POST'])
    @with_current_user
    def welcome(user):
      user.is_welcomed = True
      db.session.commit()

      return '', 204

    return user
