import json
import os
from urllib.parse import urljoin

import flask
import requests

from rainfall.db import db
from rainfall.decorators import with_current_user, with_current_site
from rainfall.models import Integration
from rainfall.site import generate_zip, zip_file_path


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


def try_create_netlify_site(netlify, token, site):
  resp = netlify.post('/api/v1/sites', token=token)
  try:
    resp.raise_for_status()
  except requests.exceptions.HTTPError as e:
    return flask.jsonify({
        'status': 500,
        'error': 'Could not create site on Netlify'
    }), 500

  site.netlify_site_id = resp.json()['id']
  db.session.add(site)
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
      deploy_site_id = flask.request.form.get('site_id')
      if deploy_site_id is None:
        return flask.jsonify({
            'status': 400,
            'error': 'No site ID provided'
        }), 400

      flask.session['deploy_site_id'] = deploy_site_id
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
        for key, value in simplified_token.items():
          setattr(user.integration, key, value)
      db.session.add(user)
      db.session.commit()

      frontend_url = flask.current_app.config['RAINFALL_FRONTEND_URL']
      if 'deploy_site_id' in flask.session:
        site_id = flask.session.pop('deploy_site_id')
        return flask.redirect(
            urljoin(frontend_url, f'/deploy/{site_id}/netlify'))

      # If the site ID is not in the session, redirect to the sites page
      return flask.redirect(urljoin(frontend_url, '/sites'))

    @oauth.route('/oauth/netlify/<site_id>/deploy', methods=['POST'])
    @with_current_user
    @with_current_site
    def deploy(site, user):
      if user.integration is None or user.integration.netlify_access_token is None:
        return flask.jsonify({
            'status': 400,
            'error': 'User has not connected Netlify'
        }), 400

      token = user.integration.to_authlib_token('netlify')

      if site.netlify_site_id is None:
        resp = try_create_netlify_site(netlify, token, site)
        if resp is not None:
          return resp

      generate_zip(flask.current_app.config['PREVIEW_DIR'], str(site.id))
      site_path = zip_file_path(flask.current_app.config['PREVIEW_DIR'],
                                str(site.id))
      zip_path = os.path.join(site_path, 'rainfall_site.zip')

      resp = netlify.post(f'/api/v1/sites/{site.netlify_site_id}/deploys',
                          token=token,
                          headers={'Content-Type': 'application/zip'},
                          data=open(zip_path, 'rb'))

      try:
        resp.raise_for_status()
      except requests.exceptions.HTTPError as e:
        return flask.jsonify({
            'status': 500,
            'error': 'Could not deploy site to Netlify'
        }), 500

      data = resp.json()
      url = data['ssl_url']
      site.netlify_url = url
      db.session.add(site)
      db.session.commit()

      return flask.jsonify({'url': url})

    return oauth
