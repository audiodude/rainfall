import os
from unittest.mock import patch

from uuid_extensions import uuid7

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.user import User
from rainfall.site import release_path, secure_filename


class FileTest:

  def test_delete_file(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      assert len(release.files) == 2
      file_id = release.files[1].id
      file_path = os.path.join(release_path(app.config['DATA_DIR'], release),
                               secure_filename(release.files[1].filename))

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/file/{str(file_id)}')

      assert rv.status == '204 NO CONTENT', rv.json

    with app.app_context():
      updated_user = db.session.get(User, BASIC_USER_ID)
      assert len(updated_user.sites[0].releases[1].files) == 1

  def test_delete_file_unwelcomed_user(self, app, basic_user):

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/file/1234')

      assert rv.status == '400 BAD REQUEST'

  def test_delete_file_not_exist(self, app, releases_user):

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/file/{uuid7()}')

      assert rv.status == '404 NOT FOUND'

  def test_delete_file_wrong_user(self, app, releases_user):
    with app.app_context():
      user = User(google_id=5678, is_welcomed=True)
      db.session.add(user)
      db.session.flush()
      user_id = user.id

      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      assert len(release.files) == 2
      file_id = release.files[1].id
      file_path = os.path.join(release_path(app.config['DATA_DIR'], release),
                               secure_filename(release.files[1].filename))
      db.session.commit()

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = user_id

      rv = client.delete(f'/api/v1/file/{str(file_id)}')

      assert rv.status == '403 FORBIDDEN'

  @patch('rainfall.blueprint.file.os.remove')
  def test_delete_file_oserror(self, mock_remove, app, releases_user):
    mock_remove.side_effect = OSError

    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      assert len(release.files) == 2
      file_id = release.files[1].id
      file_path = os.path.join(release_path(app.config['DATA_DIR'], release),
                               secure_filename(release.files[1].filename))

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/file/{str(file_id)}')

      assert rv.status == '500 INTERNAL SERVER ERROR'

  @patch('rainfall.blueprint.file.os.remove')
  def test_delete_file_already_deleted_from_filesystem(self, mock_remove, app,
                                                       releases_user):
    mock_remove.side_effect = FileNotFoundError

    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      assert len(release.files) == 2
      file_id = release.files[1].id
      file_path = os.path.join(release_path(app.config['DATA_DIR'], release),
                               secure_filename(release.files[1].filename))

    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/file/{str(file_id)}')

      assert rv.status == '204 NO CONTENT'
