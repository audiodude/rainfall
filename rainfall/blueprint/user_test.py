from unittest.mock import MagicMock, patch

import flask
import pytest
from sqlalchemy import select
import uuid

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.mastodon_credential import MastodonCredential
from rainfall.models.site import Site
from rainfall.models.user import User


class UserTest:

  def test_get_user(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get('/api/v1/user')
      assert rv.json == {
          'id': str(BASIC_USER_ID),
          'google_id': '1234',
          'mastodon_access_token': None,
          'mastodon_id': None,
          'mastodon_netloc': None,
          'name': 'Jane Doe',
          'email': 'janedoe@email.fake',
          'picture_url': 'https://pictures.fake/1234',
          'is_welcomed': False,
          'integration': None
      }

  def test_get_user_401(self, app):
    with app.test_client() as client:

      rv = client.get('/api/v1/user')
      assert rv.status == '401 UNAUTHORIZED'
      assert rv.json == {'error': 'No signed in user', 'status': 401}

  @patch('rainfall.blueprint.user.check_csrf', return_value=None)
  @patch('rainfall.blueprint.user.id_token.verify_oauth2_token')
  def test_login(self, mock_verify, mock_check_csrf, app):
    mock_verify.return_value = {
        'sub': '1234',
        'name': 'Jane Doe',
        'email': 'janedoe@email.fake',
        'picture': 'https://pictures.fake/photo-1234',
    }

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '302 FOUND'
      assert rv.headers['location'] == 'http://localhost:5173/welcome'

      user_id = flask.session['user_id']
      user = db.session.get(User, user_id)
      assert user.google_id == '1234'
      assert user.name == 'Jane Doe'
      assert user.email == 'janedoe@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'

  @patch('rainfall.blueprint.user.check_csrf', return_value=None)
  @patch('rainfall.blueprint.user.id_token.verify_oauth2_token')
  def test_login_already_welcomed(self, mock_verify, mock_check_csrf, app,
                                  basic_user):
    mock_verify.return_value = {
        'sub': '1234',
        'name': 'Jane Doe',
        'email': 'janedoe@email.fake',
        'picture': 'https://pictures.fake/photo-1234',
    }

    with app.app_context():
      basic_user.is_welcomed = True
      db.session.add(basic_user)
      db.session.commit()

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '302 FOUND'
      assert rv.headers['location'] == 'http://localhost:5173/sites'

      user_id = flask.session['user_id']
      user = db.session.get(User, user_id)
      assert user.google_id == '1234'
      assert user.name == 'Jane Doe'
      assert user.email == 'janedoe@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'
      assert user.is_welcomed

  @patch('rainfall.blueprint.user.check_csrf')
  @patch('rainfall.blueprint.user.id_token.verify_oauth2_token')
  def test_login_no_csrf(self, mock_verify, mock_check_csrf, app):
    mock_check_csrf.return_value = ({
        'status': 400,
        'error': 'Missing CSRF'
    }, 400)

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '400 BAD REQUEST'
      assert rv.json == {'status': 400, 'error': 'Missing CSRF'}

  @patch('rainfall.blueprint.user.check_csrf', return_value=None)
  @patch('rainfall.blueprint.user.id_token.verify_oauth2_token')
  def test_login_no_verify(self, mock_verify, mock_check_csrf, app):
    mock_verify.side_effect = ValueError

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '400 BAD REQUEST'
      assert rv.json == dict(status=400, error='Could not verify token')

  def test_welcome(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/user/welcome')
      assert rv.status == '204 NO CONTENT'

      user = db.session.get(User, BASIC_USER_ID)
      assert user.is_welcomed

  def test_welcome_no_user(self, app, basic_user):
    with app.test_client() as client:
      rv = client.post('/api/v1/user/welcome')
      assert rv.status == '401 UNAUTHORIZED'
      assert rv.json == {'status': 401, 'error': 'No signed in user'}

  @patch('rainfall.login.requests.post')
  def test_mastodon_init(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'client_id': 'abc_client_id',
        'client_secret': 'abc_client_secret'
    }
    mock_post.return_value = mock_response

    with app.test_client() as client:
      rv = client.post('/api/v1/mastodon/init',
                       data={'host': 'mastodon.pizza.fake'})
      assert rv.status == '302 FOUND'

    with app.app_context():
      stmt = select(MastodonCredential)
      result = db.session.execute(stmt)
      row = result.fetchone()
      assert row is not None
      assert len(row) == 1
      assert row[0] is not None
      creds = row[0]
      assert creds.netloc == 'mastodon.pizza.fake'
      assert creds.client_id == 'abc_client_id'
      assert creds.client_secret == 'abc_client_secret'

  def test_mastodon_init_existing_creds(self, app):
    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.fake',
                             client_id='abc_client_id',
                             client_secret='abc_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      rv = client.post('/api/v1/mastodon/init',
                       data={'host': 'foo.mastodon.fake'})
      assert rv.status == '302 FOUND'
      assert rv.location == (
          'https://foo.mastodon.fake/oauth/authorize?response_type=code&client_id=abc_client_id'
          '&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fapi%2Fv1%2Fmastodon%2Flogin'
      )

    with app.app_context():
      count = db.session.query(MastodonCredential.netloc).count()
      assert count == 1

  @patch('rainfall.login.requests.post')
  def test_mastodon_init_new_site_with_existing(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'client_id': 'abc_client_id',
        'client_secret': 'abc_client_secret'
    }
    mock_post.return_value = mock_response

    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.fake',
                             client_id='abc_client_id',
                             client_secret='abc_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      rv = client.post('/api/v1/mastodon/init',
                       data={'host': 'mastodon.pizza.fake'})
      assert rv.status == '302 FOUND'
      assert rv.location == (
          'https://mastodon.pizza.fake/oauth/authorize?response_type=code&client_id=abc_client_id'
          '&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fapi%2Fv1%2Fmastodon%2Flogin'
      )

    with app.app_context():
      count = db.session.query(MastodonCredential.netloc).count()
      assert count == 2

  def test_mastodon_errors(self, app):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['mastodon_login_errors'] = {
            'netloc': 'foo.mastodon.fake',
            'errors': ['There was an error.']
        }

      rv = client.get('/api/v1/mastodon/errors')
      assert rv.json == {
          'netloc': 'foo.mastodon.fake',
          'errors': ['There was an error.']
      }

      rv = client.get('/api/v1/mastodon/errors')
      assert rv.json == {'netloc': '', 'errors': []}

  @patch('rainfall.login.requests.post')
  @patch('rainfall.blueprint.user.get_mastodon_access_token',
         return_value='foo_access')
  @patch('rainfall.blueprint.user.get_mastodon_idinfo',
         return_value={
             'id': 1234,
             'email': '@foo@foo.mastodon.pizza',
             'picture': 'http://fake.fake/photo',
             'name': 'Foo Bar',
         })
  def test_mastodon_login(self, mock_idinfo, mock_access_token, mock_post, app):
    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.pizza',
                             client_id='foo_client_id',
                             client_secret='foo_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['mastodon_netloc'] = 'foo.mastodon.pizza'

      rv = client.get('/api/v1/mastodon/login',
                      query_string={'code': 'abcd1234'})

      assert rv.status == '302 FOUND'
      assert rv.location == 'http://localhost:5173/welcome'

  @patch('rainfall.login.requests.post')
  @patch('rainfall.blueprint.user.get_mastodon_access_token',
         return_value='foo_access')
  @patch('rainfall.blueprint.user.get_mastodon_idinfo',
         return_value={
             'id': 1234,
             'email': '@foo@foo.mastodon.pizza',
             'picture': 'http://fake.fake/photo',
             'name': 'Foo Bar',
         })
  def test_mastodon_login_missing_netloc(self, mock_idinfo, mock_access_token,
                                         mock_post, app):
    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.pizza',
                             client_id='foo_client_id',
                             client_secret='foo_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      rv = client.get('/api/v1/mastodon/login',
                      query_string={'code': 'abcd1234'})
      assert rv.status == '302 FOUND'
      assert rv.location == 'http://localhost:5173/mastodon'

      with client.session_transaction() as sess:
        assert sess['mastodon_login_errors'] == {
            'errors': [
                'Something went wrong, could not find host name in session.'
            ],
            'netloc': ''
        }

  @patch('rainfall.login.requests.post')
  @patch('rainfall.blueprint.user.get_mastodon_access_token', return_value=None)
  @patch('rainfall.blueprint.user.get_mastodon_idinfo',
         return_value={
             'id': 1234,
             'email': '@foo@foo.mastodon.pizza',
             'picture': 'http://fake.fake/photo',
             'name': 'Foo Bar',
         })
  def test_mastodon_login_missing_access_token(self, mock_idinfo,
                                               mock_access_token, mock_post,
                                               app):
    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.pizza',
                             client_id='foo_client_id',
                             client_secret='foo_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['mastodon_netloc'] = 'foo.mastodon.pizza'

      rv = client.get('/api/v1/mastodon/login',
                      query_string={'code': 'abcd1234'})
      assert rv.status == '302 FOUND'
      assert rv.location == 'http://localhost:5173/mastodon'

      with client.session_transaction() as sess:
        assert sess['mastodon_login_errors'] == {
            'errors': [
                'Something went wrong, could not get access token. Please try again.'
            ],
            'netloc': 'foo.mastodon.pizza'
        }

  @patch('rainfall.login.requests.post')
  @patch('rainfall.blueprint.user.get_mastodon_access_token',
         return_value='foo_access')
  @patch('rainfall.blueprint.user.get_mastodon_idinfo',
         return_value={
             'id': 1234,
             'email': '@foo@foo.mastodon.pizza',
             'picture': 'http://fake.fake/photo',
             'name': 'Foo Bar',
         })
  def test_mastodon_login_missing_code(self, mock_idinfo, mock_access_token,
                                       mock_post, app):
    with app.app_context():
      db.session.add(
          MastodonCredential(netloc='foo.mastodon.pizza',
                             client_id='foo_client_id',
                             client_secret='foo_client_secret'))
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['mastodon_netloc'] = 'foo.mastodon.pizza'

      rv = client.get(
          '/api/v1/mastodon/login',
          query_string={
              'error': 'authorize',
              'error_message': 'The user did not authorize or something'
          })
      assert rv.status == '302 FOUND'
      assert rv.location == 'http://localhost:5173/mastodon'

      with client.session_transaction() as sess:
        assert sess['mastodon_login_errors'] == {
            'errors': [
                'It looks like you denied the OAuth request. Cannot proceed with login.'
            ],
            'netloc': 'foo.mastodon.pizza'
        }

  @patch('rainfall.login.requests.post')
  @patch('rainfall.blueprint.user.get_mastodon_access_token',
         return_value='foo_access')
  @patch('rainfall.blueprint.user.get_mastodon_idinfo',
         return_value={
             'id': 1234,
             'email': '@foo@foo.mastodon.pizza',
             'picture': 'http://fake.fake/photo',
             'name': 'Foo Bar',
         })
  def test_mastodon_login_missing_creds(self, mock_idinfo, mock_access_token,
                                        mock_post, app):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['mastodon_netloc'] = 'foo.mastodon.pizza'

      rv = client.get('/api/v1/mastodon/login',
                      query_string={
                          'code': 'abcd1234',
                      })
      assert rv.status == '302 FOUND'
      assert rv.location == 'http://localhost:5173/mastodon'

      with client.session_transaction() as sess:
        assert sess['mastodon_login_errors'] == {
            'errors': [
                'Something went wrong, could not find credentials for remote app. Please try again.'
            ],
            'netloc': 'foo.mastodon.pizza'
        }
