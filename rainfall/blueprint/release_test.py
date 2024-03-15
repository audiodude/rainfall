from uuid_extensions import uuid7

import pytest

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.artwork import Artwork
from rainfall.models.release import Release
from rainfall.models.site import Site
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

  def test_create_no_user(self, app):
    with app.test_client() as client:
      rv = client.post(
          '/api/v1/release',
          json={'release': {
              'name': 'Release 1',
              'site_id': 'abc123'
          }})
      assert rv.status == '401 UNAUTHORIZED'

  def test_create_no_user_in_session(self, app, sites_user):
    with app.test_client() as client:
      rv = client.post(
          '/api/v1/release',
          json={'release': {
              'name': 'Release 1',
              'site_id': 'abc123'
          }})
      assert rv.status == '401 UNAUTHORIZED'

  def test_create_user_not_welcomed(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID
      rv = client.post(
          '/api/v1/release',
          json={'release': {
              'name': 'Release 1',
              'site_id': 'abc123'
          }})

    assert rv.status == '400 BAD REQUEST'

  def test_create_no_json(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release')
      assert rv.status == '415 UNSUPPORTED MEDIA TYPE'

  def test_create_missing_release(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release', json={'foo': 'bar'})
      assert rv.status == '400 BAD REQUEST'

  def test_create_missing_name(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release', json={'release': {}})
      assert rv.status == '400 BAD REQUEST'

  def test_create_missing_site_id(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release',
                       json={'release': {
                           'name': 'Release 1'
                       }})
      assert rv.status == '400 BAD REQUEST'

  def test_create_site_not_exist(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release',
                       json={
                           'release': {
                               'name': 'Release 1',
                               'site_id': uuid7(as_type='str')
                           }
                       })
      assert rv.status == '404 NOT FOUND'

  def test_create_site_user_mismatch(self, app, sites_user):
    with app.app_context():
      user = User(google_id='5678')
      site = Site(name='Foo')
      user.sites.append(site)
      db.session.add(user)
      db.session.add(site)
      db.session.flush()
      other_site_id = site.id
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/release',
                       json={
                           'release': {
                               'name': 'Release 1',
                               'site_id': str(other_site_id)
                           }
                       })
      assert rv.status == '401 UNAUTHORIZED'

  def test_get_release(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      release = Release(id=uuid7(), name='New Release')
      sites_user.sites[0].releases.append(release)
      db.session.flush()
      site_id = sites_user.sites[0].id
      release_id = release.id
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      print(f'/api/v1/release/{release_id}')

      rv = client.get(f'/api/v1/release/{release_id}')
      assert rv.status == '200 OK'
      assert rv.json == {
          'name': 'New Release',
          'artwork': None,
          'description': None,
          'files': [],
          'id': str(release_id),
          'site_id': str(site_id),
      }

  def test_get_release_artwork(self, app, releases_user, artwork_file):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      artwork = Artwork(filename='artwork.jpg')
      artwork.release_id = release_id = release.id
      db.session.add(release)
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get(f'/api/v1/release/{release_id}/artwork')
      assert rv.status == '200 OK'
      assert rv.text == 'not-actually-artwork'

  def test_get_release_artwork_not_found(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      release_id = release.id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get(f'/api/v1/release/{release_id}/artwork')
      assert rv.status == '404 NOT FOUND'

  def test_update_release_description(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      release_id = release.id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(f'/api/v1/release/{release_id}/description',
                       json={'description': 'New description'})
      assert rv.status == '204 NO CONTENT'
      db.session.refresh(release)
      assert release.description == 'New description'

  def test_update_release_description_no_description(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      release_id = release.id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(f'/api/v1/release/{release_id}/description',
                       json={'foo': 'bar'})
      assert rv.status == '400 BAD REQUEST'
