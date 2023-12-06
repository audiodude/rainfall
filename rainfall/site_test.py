import subprocess
from unittest.mock import patch

import pytest
from werkzeug.utils import secure_filename

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.site import build_dir, cache_dir, catalog_dir, generate_site, public_dir, release_path


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

  @patch('rainfall.site.subprocess.run')
  def test_generate_site(self, mock_subprocess, app, site_id):
    with app.app_context():
      actual = generate_site('foo/data', 'foo/preview', site_id)

      assert actual[0] is True
      assert actual[1] is None

      mock_subprocess.assert_called_once_with([
          'faircamp', '--catalog-dir',
          'foo/data/06543f11-12b6-71ea-8000-e026c63c22e2/Cool_Site_1',
          '--build-dir',
          'foo/preview/06543f11-12b6-71ea-8000-e026c63c22e2/Cool_Site_1/public',
          '--cache-dir',
          'foo/preview/06543f11-12b6-71ea-8000-e026c63c22e2/Cool_Site_1/cache',
          '--no-clean-urls'
      ],
                                              capture_output=True,
                                              check=True)

  @patch('rainfall.site.subprocess.run')
  def test_generate_site_exception(self, mock_subprocess, app, site_id):
    exc = subprocess.CalledProcessError(1, 'faircamp')
    exc.stderr = b'Standard Error'
    mock_subprocess.side_effect = exc

    with app.app_context():
      actual = generate_site('foo/data', 'foo/preview', site_id)

    assert actual[0] is False
    assert actual[1] == 'Standard Error'
