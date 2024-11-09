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
from rainfall.login import check_csrf, get_mastodon_access_token, get_mastodon_idinfo, save_or_update_mastodon_user, save_or_update_google_user, register_mastodon_app, redirect_to_instance
from rainfall.models.mastodon_credential import MastodonCredential
from rainfall.models.user import User


def session_login_error(netloc, msg):
  frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
  flask.session['mastodon_login_errors'] = {'netloc': netloc, 'errors': [msg]}
  return flask.redirect(urljoin(frontend_url, '/mastodon'))


def redirect_user_log_in(user_id):
  flask.session['user_id'] = user_id
  user = db.session.get(User, user_id)

  frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
  if user.is_welcomed:
    return flask.redirect(urljoin(frontend_url, '/sites'))
  else:
    return flask.redirect(urljoin(frontend_url, '/welcome'))


class UserBlueprintFactory:

  def __init__(self, csrf):
    self.csrf = csrf

  def get_blueprint(self):
    user = flask.Blueprint('user', __name__)

    log = logging.getLogger(__name__)

    @user.route('/user')
    @with_current_user
    def get_user(user):
      return flask.jsonify(user.serialize())

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

      return redirect_user_log_in(user_id)

    @user.route('/mastodon/init', methods=['POST'])
    def mastodon_init():
      host = flask.request.form.get('host')
      frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
      if host is None:
        return flask.jsonify(status=400, error='Host is required'), 400

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
        return session_login_error(
            netloc,
            'Could not connect to that Mastodon host. Check the spelling '
            'and make sure the host name is correct and the instance allows OAuth.'
        )

      flask.session['mastodon_netloc'] = netloc
      return redirect_to_instance(creds)

    @user.route('/mastodon/errors')
    def mastodon_errors():
      errors = flask.session.get('mastodon_login_errors')
      if errors is not None:
        del flask.session['mastodon_login_errors']
      else:
        errors = {'netloc': '', 'errors': []}
      return errors

    @self.csrf.exempt
    @user.route('/mastodon/login')
    def mastodon_login():
      netloc = flask.session.get('mastodon_netloc')
      if netloc is None:
        return session_login_error(
            '', 'Something went wrong, could not find host name in session.')
      del flask.session['mastodon_netloc']

      code = flask.request.args.get('code')
      if not code:
        return session_login_error(
            netloc,
            'It looks like you denied the OAuth request. Cannot proceed with login.'
        )

      stmt = select(MastodonCredential).where(
          MastodonCredential.netloc == netloc)
      result = db.session.execute(stmt)
      creds = result.fetchone()

      if creds is None:
        return session_login_error(
            netloc,
            'Something went wrong, could not find credentials for remote app. Please try again.'
        )
      creds = creds[0]

      access_token = get_mastodon_access_token(creds, code)
      if access_token is None:
        return session_login_error(netloc, (
            'Something went wrong, could not get access token. Please try again.'
        ))

      idinfo = get_mastodon_idinfo(creds, access_token)
      if idinfo is None:
        return session_login_error(netloc, (
            'Something went wrong, could not get user info. Please try again.'))

      user_id = save_or_update_mastodon_user(netloc, access_token, idinfo)

      return redirect_user_log_in(user_id)

    @user.route('/user/welcome', methods=['POST'])
    @with_current_user
    def welcome(user):
      user.is_welcomed = True
      db.session.commit()

      return '', 204

    return user
