from rainfall.db import db


class UserTest:

  def test_serialize(self, app, netlify_user):
    with app.app_context():
      db.session.add(netlify_user)

      actual = netlify_user.serialize()
      for field in ('id', 'google_id', 'mastodon_netloc', 'mastodon_id',
                    'mastodon_access_token', 'name', 'email', 'picture_url',
                    'is_welcomed', 'integration'):
        assert field in actual
