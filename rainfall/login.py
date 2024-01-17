from urllib.parse import urlencode, urljoin, urlunparse

import flask
import requests
from sqlalchemy import select

from rainfall.db import db
from rainfall.models.user import User
from rainfall.models.mastodon_credential import MastodonCredential


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


def save_or_update_google_user(idinfo):
  stmt = select(User).filter_by(google_id=idinfo['sub'])
  user = db.session.execute(stmt).scalar()

  if user is None:
    user = User(google_id=idinfo['sub'])

  user.email = idinfo['email']
  user.name = idinfo['name']
  user.picture_url = idinfo['picture']
  db.session.add(user)
  db.session.flush()
  user_id = user.id
  db.session.commit()

  return user_id


def register_mastodon_app(netloc):
  url = urlunparse(('https', netloc, 'api/v1/apps', '', '', ''))
  resp = requests.post(
      url,
      data={
          'client_name': flask.current_app.config['MASTODON_APP_NAME'],
          'redirect_uris': flask.current_app.config['MASTODON_REDIRECT_URL'],
          'scopes': 'read',
          'website': flask.current_app.config['MASTODON_WEBSITE']
      })

  if not resp.ok:
    logging.error(
        'Could not connect to %s, server response follows:\n---\n%s\n---',
        netloc, resp.text)
    return

  data = resp.json()
  creds = MastodonCredential(host=netloc,
                             client_key=data['client_id'],
                             client_secret=data['client_secret'])
  db.session.add(creds)
  db.session.commit()
  return creds


def redirect_to_instance(netloc, creds):
  qs = urlencode({
      'response_type': 'code',
      'client_id': creds.client_key,
      'redirect_uri': flask.current_app.config['MASTODON_REDIRECT_URL'],
  })
  url = urlunparse(('https', netloc, '/oauth/authorize', '', qs, ''))
  return flask.redirect(url)
