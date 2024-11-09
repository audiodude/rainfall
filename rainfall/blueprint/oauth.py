import json
from urllib.parse import urljoin

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models import Integration


def update_token(token, refresh_token=None, access_token=None):
  if refresh_token is not None:
    item = db.session.select(Integration).filter_by(
        netlify_refresh_token=refresh_token)
  elif access_token is not None:
    item = db.session.select(Integration).filter_by(
        netlify_access_token=access_token)
  else:
    return

  item = item.first()
  if item is None:
    return

  # Update old token
  item.netlify_access_token = token['access_token']
  item.netlify_refresh_token = token.get('refresh_token')
  item.netlify_expires_at = token['expires_at']
  db.session.add(item)
  db.session.commit()


class OauthBlueprintFactory:

  def __init__(self, oauth_lib):
    self.oauth_lib = oauth_lib

  def get_blueprint(self):
    oauth = flask.Blueprint('oauth', __name__)

    netlify = self.oauth_lib.register(
        name='netlify',
        authorize_url='https://app.netlify.com/authorize',
        authorize_params=None,
        access_token_url='https://api.netlify.com/oauth/token',
        api_base_url='https://api.netlify.com/api/v1/',
        update_token=update_token,
    )

    @oauth.route('/oauth/netlify/login', methods=['POST'])
    @with_current_user
    def login(user):
      redirect_uri = flask.url_for('oauth.authorize', _external=True)
      return netlify.authorize_redirect(redirect_uri)

    @oauth.route('/oauth/netlify/authorize')
    @with_current_user
    def authorize(user):
      token = netlify.authorize_access_token()
      token_fields = ['access_token', 'refresh_token', 'created_at']
      simplified_token = {}
      for field in token_fields:
        simplified_token[f'netlify_{field}'] = token.get(field)

      if user.integration is None:
        user.integration = Integration(**simplified_token)
      else:
        user.integration.update(**simplified_token)
      db.session.add(user)
      db.session.commit()

      frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
      return flask.redirect(urljoin(frontend_url, '/deploy/netlify'))

    return oauth
