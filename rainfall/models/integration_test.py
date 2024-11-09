from rainfall.db import db


class IntegrationTest:

  def test_serialize(self, app, netlify_user):
    with app.app_context():
      db.session.add(netlify_user)

      actual = netlify_user.integration.serialize()
      assert 'netlify_access_token' in actual
      assert 'netlify_refresh_token' in actual
      assert 'netlify_created_at' in actual
