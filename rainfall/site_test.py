import io
import os
import subprocess
from unittest.mock import patch

import pytest
from uuid_extensions import uuid7

from rainfall import object_storage
from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models import File, User
from rainfall.site import (build_dir, cache_dir, catalog_dir, delete_file,
                           generate_eno_files, generate_site, get_zip_file,
                           public_dir, release_path, rename_release_dir,
                           rename_site_dir, secure_filename, site_exists,
                           site_path)


@pytest.fixture
def site_id(app, sites_user):
  with app.app_context():
    db.session.add(sites_user)
    return str(sites_user.sites[0].id)


@pytest.fixture
def site_name(app, sites_user):
  with app.app_context():
    db.session.add(sites_user)
    return secure_filename(sites_user.sites[0].name)


class SiteTest:

  def test_catalog_dir(self, app, site_id, site_name):
    with app.app_context():
      actual = catalog_dir('foo/data', site_id)

      assert actual == f'foo/data/{str(BASIC_USER_ID)}/{site_name}'

  def test_build_dir(self, app, site_id, site_name):
    with app.app_context():
      actual = build_dir('foo/data', site_id)

      assert actual == f'foo/data/{str(BASIC_USER_ID)}/{site_name}/public'

  def test_public_dir(self, app, sites_user, site_name):
    with app.app_context():
      db.session.add(sites_user)
      actual = public_dir(sites_user.sites[0])

    assert actual == f'{str(BASIC_USER_ID)}/{site_name}/public'

  def test_cache_dir(self, app, site_id, site_name):
    with app.app_context():
      actual = cache_dir('foo/data', site_id)

      assert actual == f'foo/data/{str(BASIC_USER_ID)}/{site_name}/cache'

  def test_release_path(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      actual = release_path('/foo/data', release)

      assert actual == (
          f'/foo/data/{str(BASIC_USER_ID)}/'
          f'{secure_filename(release.site.name)}/{secure_filename(release.name)}'
      )

  def test_release_path_override(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[0]
      actual = release_path('/foo/data', release, override_name='bar')

      assert actual == (f'/foo/data/{str(BASIC_USER_ID)}/'
                        f'{secure_filename(release.site.name)}/bar')

  def test_generate_site(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      site_id = str(releases_user.sites[0].id)

      actual = generate_site(app.config['DATA_DIR'], app.config['PREVIEW_DIR'],
                             site_id)

      assert actual[0] is True
      assert actual[1] is None
      assert object_storage.path_exists(
          f'{app.config["PREVIEW_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/public'
      )
      assert not os.path.exists(
          f'{app.config["PREVIEW_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1'
      )

  @patch('rainfall.site.subprocess.run')
  def test_generate_site_exception(self, mock_subprocess, app, releases_user):
    exc = subprocess.CalledProcessError(1, 'faircamp')
    exc.stdout = 'fake faircamp stdout'
    mock_subprocess.side_effect = exc

    with app.app_context():
      db.session.add(releases_user)
      site_id = str(releases_user.sites[0].id)
      actual = generate_site(app.config['DATA_DIR'], app.config['PREVIEW_DIR'],
                             site_id)

    assert actual[0] is False
    assert actual[1] == 'fake faircamp stdout'

  def test_site_path(self, app, sites_user, site_name):
    with app.app_context():
      db.session.add(sites_user)
      actual = site_path('foo/data', sites_user.sites[0])

    assert actual == f'foo/data/{str(BASIC_USER_ID)}/{site_name}'

  def test_site_path_override_name(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      actual = site_path('foo/data', sites_user.sites[0], override_name='bar')

    assert actual == f'foo/data/{str(BASIC_USER_ID)}/bar'

  def test_secure_filename(self):
    assert secure_filename("My cool movie.mov") == "My cool movie.mov"
    assert secure_filename("../../../etc/passwd") == "etc_passwd"
    assert (secure_filename("i contain cool \xfcml\xe4uts.txt") ==
            "i contain cool umlauts.txt")
    assert secure_filename("__filename__") == "filename"
    assert secure_filename("foo$&^*)bar") == "foobar"

  def test_site_exists(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      user_id = str(sites_user.id)
      site_id = str(sites_user.sites[0].id)
      expected_path = f'{app.config["PREVIEW_DIR"]}/{user_id}/Cool Site 1/public/index.html'
      object_storage.put_object(expected_path, io.BytesIO(b''), 'text/html')
      actual = site_exists(app.config['PREVIEW_DIR'], site_id)
      assert actual

  def test_site_exists_no_site(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      site_id = str(sites_user.sites[0].id)
      actual = site_exists(app.config['PREVIEW_DIR'], site_id)
      assert not actual

  def test_get_zip_file(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      user_id = str(sites_user.id)
      site = sites_user.sites[0]
      expected_path = f'{app.config["PREVIEW_DIR"]}/{user_id}/Cool Site 1/rainfall_site.zip'
      object_storage.put_object(expected_path, io.BytesIO(b'not-a-zip'),
                                'application/zip')
      actual = get_zip_file(app.config['PREVIEW_DIR'], site)
      assert actual.read() == b'not-a-zip'

  def test_get_zip_file_not_found(self, app, sites_user):
    with app.app_context():
      db.session.add(sites_user)
      site = sites_user.sites[0]
      with pytest.raises(FileNotFoundError):
        get_zip_file(app.config['PREVIEW_DIR'], site)

  def test_delete_file(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      file = releases_user.sites[0].releases[1].files[0]
      actual = delete_file(File, str(file.id), releases_user)
      assert actual == ('', 204)

  def test_delete_file_not_found(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      actual = delete_file(File, str(uuid7()), releases_user)
      assert actual[1] == 404
      assert actual[0].json == {"error": "File does not exist", "status": 404}

  def test_delete_file_unauthorized(self, app, releases_user):
    with app.app_context():
      user = User(google_id=5678, is_welcomed=True)
      db.session.add(user)
      db.session.flush()
      user_id = user.id

      db.session.add(releases_user)
      file = releases_user.sites[0].releases[1].files[0]
      actual = delete_file(File, str(file.id), user)
      assert actual[1] == 403
      assert actual[0].json == {
          "error": "Cannot delete files for that release, unauthorized",
          "status": 401
      }

  @patch('rainfall.site.object_storage.remove_object')
  def test_delete_file_error(self, mock_remove_object, app, releases_user):
    mock_remove_object.side_effect = Exception('fake remove_object error')
    with app.app_context():
      db.session.add(releases_user)
      file = releases_user.sites[0].releases[1].files[0]
      actual = delete_file(File, str(file.id), releases_user)
      assert actual[1] == 500
      assert actual[0].json == {"error": "Could not delete file", "status": 500}

  def test_rename_release_dir(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      old_name = release.name
      old_path = f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/{old_name}'
      new_name = 'new name'
      release.name = new_name
      db.session.add(release)
      db.session.commit()

      rename_release_dir(app.config['DATA_DIR'], release, old_name)

      assert not object_storage.path_exists(old_path)
      assert object_storage.path_exists(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/new name'
      )
      assert release.name == new_name

  def test_rename_release_dir_new_exists(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      release = releases_user.sites[0].releases[1]
      old_name = release.name

      with pytest.raises(FileExistsError):
        rename_release_dir(app.config['DATA_DIR'], release, old_name)

  def test_rename_site_dir(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      site = releases_user.sites[0]
      old_name = site.name
      old_path = f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/{old_name}'
      new_name = 'new name'
      site.name = new_name
      db.session.add(site)
      db.session.commit()

      rename_site_dir(app.config['DATA_DIR'], site, old_name)

      assert not object_storage.path_exists(old_path)
      assert object_storage.path_exists(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/new name'
      )
      assert site.name == new_name

  def test_rename_site_dir_new_exists(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      site = releases_user.sites[0]
      old_name = site.name

      with pytest.raises(FileExistsError):
        rename_site_dir(app.config['DATA_DIR'], site, old_name)

  def test_generate_eno_files(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)
      site = releases_user.sites[0]

      generate_eno_files(app.config['DATA_DIR'], str(site.id))

      # Empty release, no eno file.
      assert not os.path.exists(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/Site 0 Release 1/release.eno'
      )
      assert os.path.exists(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/Site 0 Release 2/release.eno'
      )
