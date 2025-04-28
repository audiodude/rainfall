import io
import os
import time
from unittest.mock import patch

import flask

from rainfall import object_storage
from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.site import release_path, secure_filename


def assert_file_contents(app, path, contents):
  object_client = object_storage.connect(app)
  resp = None
  try:
    resp = object_client.get_object(app.config['MINIO_BUCKET'], path)
    if resp:
      resp_data = resp.read()
  finally:
    if resp is not None:
      resp.close()
  assert resp_data == contents


class UploadTest:

  def test_upload_single_file(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]
      rv = client.post(
          f'/api/v1/upload/release/{release.id}/song',
          data={'song[]': (io.BytesIO(b'not-actually-a-song'), 'song1.wav')})

      assert rv.status == '204 NO CONTENT', rv.text

      song_path = os.path.join(release_path(app.config['DATA_DIR'], release),
                               secure_filename('song1.wav'))
      assert_file_contents(app, song_path, b'not-actually-a-song')
      assert len(release.files) == 1
      assert release.files[0].filename == 'song1.wav'

  def test_upload_multiple_files(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]
      rv = client.post(f'/api/v1/upload/release/{release.id}/song',
                       data={
                           'song[]': [(io.BytesIO(b'not-actually-a-song'),
                                       'song1.wav'),
                                      (io.BytesIO(b'not-actually-a-song-2'),
                                       'song2.wav')]
                       })

      assert rv.status == '204 NO CONTENT', rv.text

      song_release_path = release_path(app.config['DATA_DIR'], release)
      song_1_path = os.path.join(song_release_path,
                                 secure_filename('song1.wav'))
      song_2_path = os.path.join(song_release_path,
                                 secure_filename('song2.wav'))
      assert_file_contents(app, song_1_path, b'not-actually-a-song')
      assert_file_contents(app, song_2_path, b'not-actually-a-song-2')

      assert len(release.files) == 2
      assert release.files[0].filename == 'song1.wav'
      assert release.files[1].filename == 'song2.wav'

  def test_upload_multiple_files_existing_multiple(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release_id = str(releases_user.sites[0].releases[1].id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/song',
                       data={
                           'song[]': [(io.BytesIO(b'not-actually-a-song'),
                                       'song1.wav'),
                                      (io.BytesIO(b'not-actually-a-song-2'),
                                       'song2.wav')]
                       })

      assert rv.status == '204 NO CONTENT', rv.text

  def test_upload_missing_songs(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release_id = str(releases_user.sites[0].releases[1].id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/song')

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_no_user_in_session(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release_id = str(releases_user.sites[0].releases[1].id)

    with app.test_client() as client:
      rv = client.post(f'/api/v1/upload/release/{release_id}/song')
      assert rv.status == '401 UNAUTHORIZED'

  def test_upload_wrong_file_type(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]

      rv = client.post(
          f'/api/v1/upload/release/{release.id}/song',
          data={'song[]': (io.BytesIO(b'not-actually-a-song'), 'song1.txt')})

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_release_art(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release = releases_user.sites[0].releases[1]
      release_id = str(release.id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/art',
                       data={
                           'artwork': (io.BytesIO(b'not-actually-artwork'),
                                       'some_artwork.jpg')
                       })

      assert rv.status == '204 NO CONTENT', rv.text
      db.session.refresh(release)
      assert release.artwork
      assert release.artwork.filename == 'some_artwork.jpg'
      file_path = os.path.join(
          release_path(flask.current_app.config['DATA_DIR'], release),
          'some_artwork.jpg')
      assert_file_contents(app, file_path, b'not-actually-artwork')

  def test_upload_release_art_no_file(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release = releases_user.sites[0].releases[1]
      release_id = str(release.id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/art')

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_release_art_wrong_type(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release = releases_user.sites[0].releases[1]
      release_id = str(release.id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/art',
                       data={
                           'artwork': (io.BytesIO(b'not-actually-a-song'),
                                       'some_artwork.wav')
                       })

      assert rv.status == '400 BAD REQUEST', rv.text

  def test_upload_release_art_delete_existing(self, app, releases_user,
                                              artwork_file):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      artwork = Artwork(filename='artwork.jpg')
      artwork.release_id = release_id = release.id
      db.session.add(release)
      db.session.commit()

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      release_id = str(release.id)
      rv = client.post(f'/api/v1/upload/release/{release_id}/art',
                       data={
                           'artwork': (io.BytesIO(b'not-actually-a-song'),
                                       'artwork1.jpg')
                       })

      assert rv.status == '204 NO CONTENT', rv.text
      db.session.refresh(release)
      assert release.artwork
      assert release.artwork.filename == 'artwork1.jpg'
      file_path = os.path.join(
          release_path(flask.current_app.config['DATA_DIR'], release),
          'artwork.jpg')
      assert not os.path.exists(file_path)

  @patch('rainfall.blueprint.upload.MP3')
  def test_upload_file_with_metadata(self, mock_mp3, app, releases_user):
    mock_instance = mock_mp3.return_value
    mock_instance.tags = {
        'TIT2': type('MockTag', (), {'text': ['Test Song']}),
        'TPE1': type('MockTag', (), {'text': ['Test Artist']}),
        'TALB': type('MockTag', (), {'text': ['Test Album']})
    }
    mock_instance.info = type('MockInfo', (), {'length': 180.0})()
    mock_instance.filename = 'song.mp3'

    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]

      rv = client.post(
          f'/api/v1/upload/release/{release.id}/song',
          data={'song[]': (io.BytesIO(b'mock-mp3-data'), 'song.mp3')})

      assert rv.status == '204 NO CONTENT', rv.text
      assert len(release.files) == 1

    uploaded_file = release.files[0]
    assert uploaded_file.filename == 'song.mp3'
    assert uploaded_file.title == 'Test Song'
    assert uploaded_file.artist == 'Test Artist'
    assert uploaded_file.album == 'Test Album'

  def test_update_file_metadata(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)

      with client.session_transaction() as sess:
        sess['user_id'] = releases_user.id

      site = releases_user.sites[0]
      release = site.releases[0]

      file = File(filename='test.mp3',
                  title='Original Title',
                  artist='Original Artist',
                  album='Original Album',
                  release_id=release.id)
      db.session.add(file)
      db.session.commit()
      file_id = str(file.id)

      new_metadata = {
          'title': 'Updated Title',
          'artist': 'Updated Artist',
          'album': 'Updated Album'
      }
      rv = client.post(f'/api/v1/file/{file_id}/metadata',
                       json=new_metadata,
                       content_type='application/json')

      assert rv.status == '204 NO CONTENT', rv.text

      db.session.refresh(file)
      assert file.title == 'Updated Title'
      assert file.artist == 'Updated Artist'
      assert file.album == 'Updated Album'

  def test_update_file_metadata_unauthorized(self, app, releases_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(releases_user)
      site = releases_user.sites[0]
      release = site.releases[0]

      file = File(filename='test.mp3',
                  title='Original Title',
                  artist='Original Artist',
                  album='Original Album',
                  release_id=release.id)
      db.session.add(file)
      db.session.commit()
      file_id = str(file.id)

      new_metadata = {
          'title': 'Updated Title',
          'artist': 'Updated Artist',
          'album': 'Updated Album'
      }
      rv = client.post(f'/api/v1/file/{file_id}/metadata',
                       json=new_metadata,
                       content_type='application/json')

      assert rv.status == '401 UNAUTHORIZED', rv.text
