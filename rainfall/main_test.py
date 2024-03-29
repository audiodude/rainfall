from unittest.mock import patch
import io
import os

from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.conftest import BASIC_USER_ID
from rainfall.main import create_app


def assert_file_contents(file_path, contents):
  with open(file_path, 'r') as f:
    assert f.read() == contents


class MainTest:

  def test_create_app_no_errors(self):
    create_app()

  def test_upload_single_file(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]
      rv = client.post(
          '/api/v1/upload',
          data={
              'release_id': str(release.id),
              'song[]': (io.BytesIO(b'not-actually-a-song'), 'song1.wav')
          })

      assert rv.status == '204 NO CONTENT', rv.text

      song_path = os.path.join(app.config['DATA_DIR'], str(releases_user.id),
                               secure_filename(site.name),
                               secure_filename(release.name),
                               secure_filename('song1.wav'))
      assert_file_contents(song_path, 'not-actually-a-song')

      assert len(release.files) == 1
      assert release.files[0].filename == 'song1.wav'

  def test_upload_multiple_files(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]
      rv = client.post('/api/v1/upload',
                       data={
                           'release_id':
                               str(release.id),
                           'song[]': [(io.BytesIO(b'not-actually-a-song'),
                                       'song1.wav'),
                                      (io.BytesIO(b'not-actually-a-song-2'),
                                       'song2.wav')]
                       })

      assert rv.status == '204 NO CONTENT', rv.text

      release_path = os.path.join(app.config['DATA_DIR'], str(releases_user.id),
                                  secure_filename(site.name),
                                  secure_filename(release.name))
      song_1_path = os.path.join(release_path, secure_filename('song1.wav'))
      song_2_path = os.path.join(release_path, secure_filename('song2.wav'))
      assert_file_contents(song_1_path, 'not-actually-a-song')
      assert_file_contents(song_2_path, 'not-actually-a-song-2')

      assert len(release.files) == 2
      assert release.files[0].filename == 'song1.wav'
      assert release.files[1].filename == 'song2.wav'

  def test_upload_multiple_files_existing_multiple(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      rv = client.post('/api/v1/upload',
                       data={
                           'release_id':
                               str(releases_user.sites[0].releases[1].id),
                           'song[]': [(io.BytesIO(b'not-actually-a-song'),
                                       'song1.wav'),
                                      (io.BytesIO(b'not-actually-a-song-2'),
                                       'song2.wav')]
                       })

      assert rv.status == '204 NO CONTENT', rv.text

  def test_upload_missing_release_id(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      rv = client.post('/api/v1/upload',
                       data={
                           'release_id':
                               str(releases_user.sites[0].releases[1].id),
                       })

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_missing_songs(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      rv = client.post(
          '/api/v1/upload',
          data={'song[]': (io.BytesIO(b'not-actually-a-song'), 'song1.wav')})

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_no_user(self, app):
    with app.test_client() as client:
      rv = client.post('/api/v1/upload')
      assert rv.status == '404 NOT FOUND'

  def test_upload_no_user_in_session(self, app, releases_user):
    with app.test_client() as client:
      rv = client.post('/api/v1/upload')
      assert rv.status == '404 NOT FOUND'

  def test_upload_wrong_file_type(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]
      rv = client.post(
          '/api/v1/upload',
          data={
              'release_id': str(release.id),
              'song[]': (io.BytesIO(b'not-actually-a-song'), 'song1.txt')
          })

      assert rv.status == '400 BAD REQUEST', rv.text
