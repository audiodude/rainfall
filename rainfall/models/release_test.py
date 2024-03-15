from rainfall.db import db


class ReleaseTest:

  def test_serialize(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]

      actual = release.serialize()
      assert 'id' in actual
      assert 'site_id' in actual
      assert 'name' in actual
      assert 'files' in actual
      assert len(actual['files']) != 0
      assert 'artwork' in actual
