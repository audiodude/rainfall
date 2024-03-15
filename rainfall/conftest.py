import os
import uuid

import flask
import pytest
from uuid_extensions import uuid7

from rainfall.db import db
from rainfall.main import create_app
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.models.user import User
from rainfall.site import release_path

BASIC_USER_ID = uuid.UUID('06543f11-12b6-71ea-8000-e026c63c22e2')


@pytest.fixture
def app():
  app = create_app()
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
      'SQLALCHEMY_TEST_DATABASE_URI']
  app.config['TESTING'] = True
  db.init_app(app)

  with app.app_context():
    db.create_all()

  yield app

  with app.app_context():
    db.drop_all()


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
def sites_user(app, welcomed_user):
  with app.app_context():
    db.session.add(welcomed_user)
    welcomed_user.sites.append(Site(name='Cool Site 1'))
    welcomed_user.sites.append(Site(name='Another Cool Site'))

    db.session.add(welcomed_user)
    db.session.commit()

  return welcomed_user


@pytest.fixture
def releases_user(app, sites_user):
  with app.app_context():
    db.session.add(sites_user)
    sites_user.sites[0].releases.append(Release(name='Site 0 Release 1'))
    sites_user.sites[0].releases.append(
        Release(name='Site 0 Release 2',
                files=[
                    File(filename='s0_r1_file_0.wav'),
                    File(filename='s0_r1_file_1.aiff')
                ]))
    sites_user.sites[1].releases.append(Release(name='Site 1 Release 1'))

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
    os.makedirs(release_path(flask.current_app.config['DATA_DIR'], release),
                exist_ok=True)
    file_path = os.path.join(
        release_path(flask.current_app.config['DATA_DIR'], release),
        'artwork.jpg')
    db.session.commit()

  with open(file_path, 'w') as f:
    f.write('not-actually-artwork')

  yield file_path

  try:
    os.remove(file_path)
  except:
    pass
