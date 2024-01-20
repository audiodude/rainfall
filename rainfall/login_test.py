from unittest.mock import MagicMock, patch

from werkzeug.http import dump_cookie
from sqlalchemy import select, text

from rainfall.db import db
from rainfall.login import check_csrf, get_mastodon_access_token, get_mastodon_idinfo, save_or_update_google_user, save_or_update_mastodon_user, redirect_to_instance, register_mastodon_app
from rainfall.models.mastodon_credential import MastodonCredential
from rainfall.models.user import User


class LoginTest:

  def test_check_csrf(self, app):
    header = dump_cookie('g_csrf_token', 'footoken')
    with app.test_request_context(data={'g_csrf_token': 'footoken'},
                                  environ_base={'HTTP_COOKIE': header}):
      actual = check_csrf()
      assert actual is None

  def test_check_csrf_missing_cookie(self, app):
    with app.test_request_context(data={'g_csrf_token': 'footoken'}):
      actual = check_csrf()
      assert len(actual) == 2
      response, status = actual
      assert status == 400
      assert response.mimetype == 'application/json'
      assert response.get_json() == {
          'status': 400,
          'error': 'No CSRF token in Cookie'
      }

  def test_check_csrf_missing_post(self, app):
    header = dump_cookie('g_csrf_token', 'footoken')
    with app.test_request_context(environ_base={'HTTP_COOKIE': header}):
      actual = check_csrf()
      assert len(actual) == 2
      response, status = actual
      assert status == 400
      assert response.mimetype == 'application/json'
      assert response.get_json() == {
          'status': 400,
          'error': 'No CSRF token in post body'
      }

  def test_check_csrf_mismatch(self, app):
    header = dump_cookie('g_csrf_token', 'footoken')
    with app.test_request_context(data={'g_csrf_token': 'bartoken'},
                                  environ_base={'HTTP_COOKIE': header}):
      actual = check_csrf()
      assert len(actual) == 2
      response, status = actual
      assert status == 400
      assert response.mimetype == 'application/json'
      assert response.get_json() == {
          'status': 400,
          'error': 'Failed to verify double submit cookie'
      }

  def test_save_or_update_google_user_save(self, app):
    with app.app_context():
      actual = save_or_update_google_user({
          'sub': '1234',
          'name': 'Jane Doe',
          'email': 'janedoe@email.fake',
          'picture': 'https://pictures.fake/photo-1234'
      })

      user = db.session.get(User, actual)
      assert user.google_id == '1234'
      assert user.mastodon_id is None
      assert user.name == 'Jane Doe'
      assert user.email == 'janedoe@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'

  def test_save_or_update_google_user_update(self, app):
    with app.app_context():
      existing = User(google_id='1234')
      db.session.add(existing)
      db.session.flush()
      user_id = existing.id

      actual = save_or_update_google_user({
          'sub': '1234',
          'name': 'Jane Deer',
          'email': 'janedeer@email.fake',
          'picture': 'https://pictures.fake/photo-1234-jpg'
      })

      user = db.session.get(User, user_id)
      assert user.google_id == '1234'
      assert user.name == 'Jane Deer'
      assert user.email == 'janedeer@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234-jpg'

  def test_save_or_update_mastodon_user_save(self, app):
    with app.app_context():
      actual = save_or_update_mastodon_user(
          'mastodon.fake', 'access_1234', {
              'id': '1234',
              'name': 'Jane Doe',
              'email': '@janedoe@mastodon.fake',
              'picture': 'https://pictures.fake/photo-1234'
          })

      user = db.session.get(User, actual)
      assert user.google_id is None
      assert user.mastodon_id == '1234'
      assert user.mastodon_netloc == 'mastodon.fake'
      assert user.mastodon_access_token == 'access_1234'
      assert user.name == 'Jane Doe'
      assert user.email == '@janedoe@mastodon.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'

  def test_save_or_update_mastodon_user_update(self, app):
    with app.app_context():
      existing = User(mastodon_id='1234',
                      mastodon_access_token='token',
                      mastodon_netloc='mastodon.fake')
      db.session.add(existing)
      db.session.flush()
      user_id = existing.id

      actual = save_or_update_mastodon_user(
          'mastodon.fake', 'access_1234', {
              'id': '1234',
              'name': 'Jane Deer',
              'email': 'janedeer@email.fake',
              'picture': 'https://pictures.fake/photo-1234-jpg'
          })

      user = db.session.get(User, user_id)
      assert user.google_id is None
      assert user.mastodon_id == '1234'
      assert user.mastodon_netloc == 'mastodon.fake'
      assert user.mastodon_access_token == 'access_1234'
      assert user.name == 'Jane Deer'
      assert user.email == 'janedeer@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234-jpg'

  @patch('rainfall.login.requests.post')
  def test_register_mastodon_app(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'client_id': 'abc_client_id',
        'client_secret': 'abc_client_secret'
    }
    mock_post.return_value = mock_response

    with app.app_context():
      actual = register_mastodon_app('mastodon.pizza.fake')

      assert actual.netloc == 'mastodon.pizza.fake'
      assert actual.client_id == 'abc_client_id'
      assert actual.client_secret == 'abc_client_secret'

    mock_post.assert_called_once_with(
        'https://mastodon.pizza.fake/api/v1/apps',
        data={
            'client_name': 'Rainfall Dev',
            'redirect_uris': 'http://localhost:5000/api/v1/mastodon/login',
            'scopes': 'read',
            'website': 'http://localhost:5000'
        })

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

  @patch('rainfall.login.requests.post')
  def test_register_mastodon_app_non_200(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_post.return_value = mock_response

    with app.app_context():
      actual = register_mastodon_app('mastodon.pizza.fake')

    assert actual is None

  @patch('rainfall.login.flask.redirect')
  def test_redirect_to_instance(self, mock_redirect, app):
    creds = MastodonCredential(netloc='mastodon.pizza.fake',
                               client_id='xyz_client_key',
                               client_secret='xyz_client_secret')

    with app.app_context():
      redirect_to_instance(creds)

    mock_redirect.assert_called_once_with(
        'https://mastodon.pizza.fake/oauth/authorize?response_type=code&'
        'client_id=xyz_client_key&redirect_uri=http%3A%2F%2Flocalhost%3A5000'
        '%2Fapi%2Fv1%2Fmastodon%2Flogin')

  @patch('rainfall.login.requests.post')
  def test_get_mastodon_access_token(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'access_token': 'access_xyz',
    }
    mock_post.return_value = mock_response

    creds = MastodonCredential(netloc='mastodon.pizza.fake',
                               client_id='xyz_client_key',
                               client_secret='xyz_client_secret')

    with app.app_context():
      actual = get_mastodon_access_token(creds, 'abc123')

    assert actual == 'access_xyz'

  @patch('rainfall.login.requests.get')
  def test_get_mastodon_idinfo(self, mock_post, app):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'id': '5678',
        'username': 'foobar',
        'display_name': 'Foo Bar',
        'avatar': 'https://pictures.fake/photo.jpg',
    }
    mock_post.return_value = mock_response

    creds = MastodonCredential(netloc='mastodon.pizza.fake',
                               client_id='xyz_client_key',
                               client_secret='xyz_client_secret')

    actual = get_mastodon_idinfo(creds, 'access_1234')

    assert actual == {
        'email': '@foobar@mastodon.pizza.fake',
        'id': '5678',
        'name': 'Foo Bar',
        'picture': 'https://pictures.fake/photo.jpg'
    }
