import pytest

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.user import User


class ReleaseTest:

  def test_create(self, app, site_id):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(
          '/api/v1/release',
          json={'release': {
              'name': 'Release 1',
              'site_id': site_id
          }})
      print(rv.text)
      assert rv.status == '204 NO CONTENT'

    with app.app_context():
      user = db.session.get(User, BASIC_USER_ID)
      sites = user.sites
      assert len(sites) == 2
      releases = user.sites[0].releases
      assert len(releases) == 1
      assert releases[0].name == 'Release 1'
