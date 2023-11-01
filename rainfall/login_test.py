from werkzeug.http import dump_cookie

from rainfall.login import check_csrf
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
