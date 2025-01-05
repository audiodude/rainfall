import io
import os
import subprocess
from unittest.mock import patch

import pytest

from rainfall import object_storage
from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models import File
from rainfall.site import (build_dir, cache_dir, catalog_dir, generate_site,
                           public_dir, release_path, secure_filename, site_path)


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
