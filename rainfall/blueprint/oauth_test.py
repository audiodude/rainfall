from functools import partial
from unittest.mock import MagicMock, patch, ANY, mock_open

import flask
import requests

from rainfall.blueprint.oauth import OauthBlueprintFactory, update_token
from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models import Integration


class OauthTest:
  TEST_TOKEN = {
      'access_token': 'test-access-token',
      'refresh_token': 'test-refresh-token',
      'created_at': 5000,
  }

  def test_register_netlify(self):
    mock_oauth = MagicMock()
    blueprint = OauthBlueprintFactory(mock_oauth).get_blueprint()

    mock_oauth.register.assert_called_with(
        name='netlify',
        authorize_url='https://app.netlify.com/authorize',
        authorize_params=None,
        access_token_url='https://api.netlify.com/oauth/token',
        api_base_url='https://api.netlify.com/api/v1/',
        update_token=ANY,
    )

  def test_login(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.test_client() as client:
      app.mock_remote_app.authorize_redirect.return_value = flask.redirect(
          'http://netlify.fake/oauth')

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(
          '/api/v1/oauth/netlify/login',
          data={'site_id': '51af3339-b5a7-405c-a29e-c2aa6d28f5d0'})

      assert response.status == '302 FOUND'
      assert response.location == 'http://netlify.fake/oauth'
      app.mock_remote_app.authorize_redirect.assert_called_with(
          'http://localhost/api/v1/oauth/netlify/authorize')

  def test_login_no_user(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.test_client() as client:
      app.mock_remote_app.authorize_redirect.return_value = flask.redirect(
          'http://netlify.fake/oauth')

      response = client.post('/api/v1/oauth/netlify/login')
      assert response.status == '401 UNAUTHORIZED'

  def test_login_missing_site(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.test_client() as client:
      app.mock_remote_app.authorize_redirect.return_value = flask.redirect(
          'http://netlify.fake/oauth')

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post('/api/v1/oauth/netlify/login')

      assert response.status == '400 BAD REQUEST'
      app.mock_remote_app.authorize_redirect.assert_not_called()

  def test_authorize(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.app_context(), app.test_client() as client:
      app.mock_remote_app.authorize_access_token.return_value = self.TEST_TOKEN

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID
        sess['deploy_site_id'] = '51af3339-b5a7-405c-a29e-c2aa6d28f5d0'

      response = client.get('/api/v1/oauth/netlify/authorize')

      assert response.status == '302 FOUND'
      assert response.location == 'http://localhost:5173/deploy/51af3339-b5a7-405c-a29e-c2aa6d28f5d0/netlify'

      actual = db.session.query(Integration).first()
      assert actual.netlify_access_token == 'test-access-token'
      assert actual.netlify_refresh_token == 'test-refresh-token'
      assert actual.netlify_created_at == 5000

  def test_authorize_existing_integration(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.app_context(), app.test_client() as client:
      app.mock_remote_app.authorize_access_token.return_value = self.TEST_TOKEN
      basic_user.integration = Integration(
          netlify_access_token='old-access-token',
          netlify_refresh_token='old-refresh-token',
          netlify_created_at=1234)
      db.session.add(basic_user)
      db.session.commit()

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID
        sess['deploy_site_id'] = '51af3339-b5a7-405c-a29e-c2aa6d28f5d0'

      response = client.get('/api/v1/oauth/netlify/authorize')

      assert response.status == '302 FOUND'
      assert response.location == 'http://localhost:5173/deploy/51af3339-b5a7-405c-a29e-c2aa6d28f5d0/netlify'

      actual = db.session.query(Integration).first()
      assert actual.netlify_access_token == 'test-access-token'
      assert actual.netlify_refresh_token == 'test-refresh-token'
      assert actual.netlify_created_at == 5000

  def test_authorize_no_site_id(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.app_context(), app.test_client() as client:
      app.mock_remote_app.authorize_access_token.return_value = self.TEST_TOKEN

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.get('/api/v1/oauth/netlify/authorize')

      assert response.status == '302 FOUND'
      assert response.location == 'http://localhost:5173/sites'

  def test_authorize_no_user(self, app, basic_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    with app.app_context(), app.test_client() as client:
      app.mock_remote_app.authorize_access_token.return_value = self.TEST_TOKEN

      response = client.get('/api/v1/oauth/netlify/authorize')

      assert response.status == '401 UNAUTHORIZED'

  @patch('rainfall.blueprint.oauth.generate_zip')
  @patch('rainfall.blueprint.oauth.open',
         new_callable=partial(mock_open, read_data=b'xyz-test-not-a-zip'),
         create=True)
  def test_deploy(self, m_open, mock_generate_zip, app, sites_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    m_open.return_value = b'xyz-test-not-a-zip'
    mock_json_1 = {'id': 'abc-netlify-id'}
    mock_response_1 = MagicMock()
    mock_response_1.json.return_value = mock_json_1
    mock_json_2 = {'ssl_url': 'https://netlify.fake/site'}
    mock_response_2 = MagicMock()
    mock_response_2.json.return_value = mock_json_2

    app.mock_remote_app.post.side_effect = (mock_response_1, mock_response_2)

    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id
      sites_user.integration = Integration(
          netlify_access_token='test-access-token',
          netlify_refresh_token='test-refresh-token',
          netlify_created_at=5000)

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      mock_generate_zip.assert_called_once_with(app.config['PREVIEW_DIR'],
                                                str(site_id))
      assert response.status == '200 OK'
      assert response.json == {'url': 'https://netlify.fake/site'}
      app.mock_remote_app.post.assert_called_with(
          '/api/v1/sites/abc-netlify-id/deploys',
          token={
              'access_token': 'test-access-token',
              'refresh_token': 'test-refresh-token',
              'created_at': 5000,
              'token_type': 'Bearer',
              'scope': 'public'
          },
          headers={'Content-Type': 'application/zip'},
          data=b'xyz-test-not-a-zip')

  @patch('rainfall.blueprint.oauth.generate_zip')
  @patch('rainfall.blueprint.oauth.open',
         new_callable=partial(mock_open, read_data=b'xyz-test-not-a-zip'),
         create=True)
  def test_deploy_existing_site(self, m_open, mock_generate_zip, app,
                                sites_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    m_open.return_value = b'xyz-test-not-a-zip'
    mock_json_2 = {'ssl_url': 'https://netlify.fake/site'}
    mock_response_2 = MagicMock()
    mock_response_2.json.return_value = mock_json_2
    app.mock_remote_app.post.return_value = mock_response_2

    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id
      sites_user.sites[0].netlify_site_id = 'abc-netlify-id'
      sites_user.integration = Integration(
          netlify_access_token='test-access-token',
          netlify_refresh_token='test-refresh-token',
          netlify_created_at=5000)

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      mock_generate_zip.assert_called_once_with(app.config['PREVIEW_DIR'],
                                                str(site_id))
      assert response.status == '200 OK'
      assert response.json == {'url': 'https://netlify.fake/site'}
      app.mock_remote_app.post.assert_called_with(
          '/api/v1/sites/abc-netlify-id/deploys',
          token={
              'access_token': 'test-access-token',
              'refresh_token': 'test-refresh-token',
              'created_at': 5000,
              'token_type': 'Bearer',
              'scope': 'public'
          },
          headers={'Content-Type': 'application/zip'},
          data=b'xyz-test-not-a-zip')

  def test_deploy_create_site_error(self, app, sites_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    error_resp = MagicMock()
    error_resp.raise_for_status.side_effect = requests.exceptions.HTTPError
    app.mock_remote_app.post.return_value = error_resp

    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id
      sites_user.integration = Integration(
          netlify_access_token='test-access-token',
          netlify_refresh_token='test-refresh-token',
          netlify_created_at=5000)

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      assert response.status == '500 INTERNAL SERVER ERROR'

  def test_deploy_no_user(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      assert response.status == '401 UNAUTHORIZED'

  def test_deploy_no_site(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(
          '/api/v1/oauth/netlify/c6294291-a5a0-46fc-863d-d08cd9c3d671/deploy')

      assert response.status == '404 NOT FOUND'

  def test_deploy_no_netlify_token(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      assert response.status == '400 BAD REQUEST'
      assert 'error' in response.json

  @patch('rainfall.blueprint.oauth.generate_zip')
  @patch('rainfall.blueprint.oauth.open',
         new_callable=partial(mock_open, read_data=b'xyz-test-not-a-zip'),
         create=True)
  def test_deploy_netlify_error(self, m_open, mock_generate_zip, app,
                                sites_user):
    # We stash the mock OAuth lib in the app object
    app.mock_oauth.assert_called_once_with(app)

    m_open.return_value = b'xyz-test-not-a-zip'
    mock_json_1 = {'id': 'abc-netlify-id'}
    mock_response_1 = MagicMock()
    mock_response_1.json.return_value = mock_json_1
    mock_response_2 = MagicMock()
    mock_response_2.raise_for_status.side_effect = requests.exceptions.HTTPError

    app.mock_remote_app.post.side_effect = (mock_response_1, mock_response_2)

    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id
      sites_user.integration = Integration(
          netlify_access_token='test-access-token',
          netlify_refresh_token='test-refresh-token',
          netlify_created_at=5000)

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      response = client.post(f'/api/v1/oauth/netlify/{site_id}/deploy')

      mock_generate_zip.assert_called_once_with(app.config['PREVIEW_DIR'],
                                                str(site_id))
      assert response.status == '500 INTERNAL SERVER ERROR'
      assert 'error' in response.json

  def test_update_token_refresh_token(self, app, sites_user):
    with app.app_context():
      sites_user.integration = Integration(
          netlify_refresh_token='refresh-token-1')
      db.session.add(sites_user)
      db.session.commit()

      update_token(self.TEST_TOKEN, refresh_token='refresh-token-1')

      db.session.add(sites_user)
      assert sites_user.integration.netlify_access_token == 'test-access-token'
      assert sites_user.integration.netlify_refresh_token == 'test-refresh-token'
      assert sites_user.integration.netlify_created_at == 5000

  def test_update_token_access_token(self, app, sites_user):
    with app.app_context():
      sites_user.integration = Integration(
          netlify_access_token='access-token-1')
      db.session.add(sites_user)
      db.session.commit()

      update_token(self.TEST_TOKEN, access_token='access-token-1')

      db.session.add(sites_user)
      assert sites_user.integration.netlify_access_token == 'test-access-token'
      assert sites_user.integration.netlify_refresh_token == 'test-refresh-token'
      assert sites_user.integration.netlify_created_at == 5000
