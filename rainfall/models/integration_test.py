from rainfall.db import db


class IntegrationTest:

  def test_serialize(self, app, netlify_user):
    with app.app_context():
      db.session.add(netlify_user)

      actual = netlify_user.integration.serialize()
      assert 'has_netlify_token' in actual
