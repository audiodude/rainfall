import logging
from urllib.parse import urlencode, urljoin, urlunparse

import flask
import requests
from sqlalchemy import select

from rainfall.db import db
from rainfall.models.mastodon_credential import MastodonCredential
from rainfall.models.user import User

log = logging.getLogger(__name__)


def check_csrf():
  # This is NOT the general CSRF protection provided by SeaSurf. This is a
  # specific CSRF protection that Google login implements.
  csrf_token_cookie = flask.request.cookies.get('g_csrf_token')
  if not csrf_token_cookie:
    return flask.jsonify(status=400, error='No CSRF token in Cookie'), 400
  csrf_token_body = flask.request.form.get('g_csrf_token')
  if not csrf_token_body:
    return flask.jsonify(status=400, error='No CSRF token in post body'), 400
  if csrf_token_cookie != csrf_token_body:
    return flask.jsonify(status=400,
                         error='Failed to verify double submit cookie'), 400


def update_user_info(user, idinfo):
  user.email = idinfo['email']
  user.name = idinfo['name']
  user.picture_url = idinfo['picture']
  db.session.add(user)
  db.session.flush()
  user_id = user.id
  db.session.commit()

  return user_id

def save_or_update_google_user(idinfo):
  stmt = select(User).filter_by(google_id=idinfo['sub'])
  user = db.session.execute(stmt).scalar()

  if user is None:
    user = User(google_id=idinfo['sub'])

  return update_user_info(user, idinfo)


def save_or_update_mastodon_user(netloc, access_token, idinfo):
  stmt = select(User).filter_by(mastodon_netloc=netloc, mastodon_id=idinfo['id'])
  user = db.session.execute(stmt).scalar()

  if user is None:
    user = User(mastodon_id=idinfo['id'], mastodon_netloc=netloc, mastodon_access_token=access_token)

  user.mastodon_access_token = access_token
  return update_user_info(user, idinfo)


def register_mastodon_app(netloc):
  url = urlunparse(('https', netloc, 'api/v1/apps', '', '', ''))
  try:
    resp = requests.post(
        url,
        data={
            'client_name': flask.current_app.config['MASTODON_APP_NAME'],
            'redirect_uris': flask.current_app.config['MASTODON_REDIRECT_URL'],
            'scopes': 'read',
            'website': flask.current_app.config['MASTODON_WEBSITE']
        })
  except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
    log.warning('Could not connect to %s for Mastodon login', netloc)
    return

  if not resp.ok:
    log.error('Error response from %s:\n---\n%s\n---', netloc, resp.text)
    return

  data = resp.json()
  creds = MastodonCredential(netloc=netloc,
                             client_id=data['client_id'],
                             client_secret=data['client_secret'])
  db.session.add(creds)
  db.session.commit()
  return creds


def redirect_to_instance(creds):
  qs = urlencode({
      'response_type': 'code',
      'client_id': creds.client_id,
      'redirect_uri': flask.current_app.config['MASTODON_REDIRECT_URL'],
  })
  url = urlunparse(('https', creds.netloc, '/oauth/authorize', '', qs, ''))
  return flask.redirect(url)


def get_mastodon_access_token(creds, code):
  url = urlunparse(('https', creds.netloc, '/oauth/token', '', '', ''))
  try:
    resp = requests.post(
        url,
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'redirect_uri': flask.current_app.config['MASTODON_REDIRECT_URL'],
            'scope': 'read',
        })
  except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
    log.warning('Could not connect to %s for Mastodon access token', creds.netloc)
    return None

  if not resp.ok:
    log.error('Error response while gettting Mastodon access token from %s\n---\n%s\n---', creds.netloc, resp.text)
    return None

  return resp.json()['access_token']


def get_mastodon_idinfo(creds, access_token):
  url = urlunparse(('https', creds.netloc, '/api/v1/accounts/verify_credentials', '', '', ''))
  try:
    resp = requests.get(url,
                         headers={'Authorization': f'Bearer {access_token}'})
  except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
    log.warning('Could not connect to %s for Mastodon id', creds.netloc)
    return None

  if not resp.ok:
    log.error('Error response while gettting Mastodon user info from %s\n---\n%s\n---', creds.netloc, resp.text)
    return None

  data = resp.json()
  return {
      'id': data['id'],
      'email': f'@{data['username']}@{creds.netloc}',
      'name': data['display_name'],
      'picture': data['avatar'],
  }
