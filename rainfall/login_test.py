from werkzeug.http import dump_cookie

from sqlalchemy import text

from rainfall.db import db
from rainfall.login import check_csrf, save_or_update_google_user
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
