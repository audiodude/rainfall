import io
import logging
import os
import shutil
import uuid
from unittest.mock import MagicMock, patch

import flask
import pytest
from uuid_extensions import uuid7

from rainfall import object_storage
from rainfall.db import db
from rainfall.main import create_app, init_object_storage
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.models.integration import Integration
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.models.user import User
from rainfall.site import release_path, site_path
from rainfall.test_constants import (TEST_FILE_PATH, TEST_MINIO_BUCKET,
                                     TEST_WAV_PATH)

BASIC_USER_ID = uuid.UUID('06543f11-12b6-71ea-8000-e026c63c22e2')

urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.setLevel(logging.WARNING)


@pytest.fixture
def app():
  with patch('rainfall.main.OAuth') as mock_oauth:
    mock_oauth_lib = MagicMock()
    mock_oauth.return_value = mock_oauth_lib
    mock_remote_app = MagicMock()
    mock_oauth_lib.register.return_value = mock_remote_app

    app = create_app()

    app.mock_oauth = mock_oauth
    app.mock_remote_app = mock_remote_app

  app.config['MINIO_BUCKET'] = TEST_MINIO_BUCKET
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
      'SQLALCHEMY_TEST_DATABASE_URI']
  app.config['TESTING'] = True

  db.init_app(app)
  init_object_storage(app)

  os.makedirs(app.config['DATA_DIR'], exist_ok=True)
  os.makedirs(app.config['PREVIEW_DIR'], exist_ok=True)

  with app.app_context():
    db.create_all()

  yield app

  with app.app_context():
    db.drop_all()
    object_storage.rmtree(None)
    shutil.rmtree(app.config['DATA_DIR'])
    shutil.rmtree(app.config['PREVIEW_DIR'])


@pytest.fixture
def basic_user(app):
  with app.app_context():
    basic_user = User(id=BASIC_USER_ID,
                      google_id='1234',
                      name='Jane Doe',
                      email='janedoe@email.fake',
                      picture_url='https://pictures.fake/1234')
    db.session.add(basic_user)
    db.session.commit()

  return basic_user


@pytest.fixture
def welcomed_user(app, basic_user):
  with app.app_context():
    basic_user.is_welcomed = True
    db.session.add(basic_user)
    db.session.commit()

  return basic_user


@pytest.fixture
def netlify_user(app, basic_user):
  with app.app_context():
    basic_user.integration = Integration(
        netlify_access_token='netlify_access_token',
        netlify_refresh_token='netlify_refresh_token',
        netlify_created_at=1234)
    db.session.add(basic_user)
    db.session.commit()

  return basic_user


@pytest.fixture
def sites_user(app, welcomed_user):
  with app.app_context():
    db.session.add(welcomed_user)

    site_1 = Site(name='Cool Site 1')
    welcomed_user.sites.append(site_1)

    site_2 = Site(name='Another Cool Site')
    welcomed_user.sites.append(site_2)

    db.session.add(welcomed_user)
    db.session.commit()

  return welcomed_user


@pytest.fixture
def releases_user(app, sites_user):
  with app.app_context():
    db.session.add(sites_user)

    release_1 = Release(name='Site 0 Release 1')
    sites_user.sites[0].releases.append(release_1)

    release_2 = Release(name='Site 0 Release 2',
                        files=[
                            File(filename='s0_r1_file_0.wav'),
                            File(filename='s0_r1_file_1.wav')
                        ])

    with open(TEST_WAV_PATH, 'rb') as f:
      object_storage.put_object(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/Site 0 Release 2/s0_r1_file_0.wav',
          f, 'audio/wav')
    with open(TEST_WAV_PATH, 'rb') as f:
      object_storage.put_object(
          f'{app.config["DATA_DIR"]}/06543f11-12b6-71ea-8000-e026c63c22e2/Cool Site 1/Site 0 Release 2/s0_r1_file_1.wav',
          f, 'audio/wav')
    sites_user.sites[0].releases.append(release_2)

    release_3 = Release(name='Site 1 Release 1')
    sites_user.sites[1].releases.append(release_3)

    db.session.add(sites_user)
    db.session.commit()

  return sites_user


@pytest.fixture
def site_id(app, sites_user):
  with app.app_context():
    db.session.add(sites_user)
    return sites_user.sites[0].id


@pytest.fixture
def artwork_file(app, releases_user):
  with app.app_context():
    db.session.add(releases_user)
    release = releases_user.sites[0].releases[0]
    release.artwork = Artwork(id=uuid7(), filename='artwork.jpg')
    file_path = os.path.join(
        release_path(flask.current_app.config['DATA_DIR'], release),
        'artwork.jpg')
    db.session.commit()
    object_storage.put_object(file_path, io.BytesIO(b'not-actually-artwork'),
                              'image/jpeg')

  yield file_path

  try:
    object_storage.delete_object(file_path)
  except:
    pass
