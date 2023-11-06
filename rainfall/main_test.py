from unittest.mock import patch

import flask
import pytest
import uuid

from rainfall.db import db
from rainfall.models.site import Site
from rainfall.models.user import User

BASIC_USER_ID = uuid.UUID('06543f11-12b6-71ea-8000-e026c63c22e2')


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


class MainTest:

  def test_get_user(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get('/api/v1/user')
      assert rv.json == {
          'id': str(BASIC_USER_ID),
          'google_id': '1234',
          'name': 'Jane Doe',
          'email': 'janedoe@email.fake',
          'picture_url': 'https://pictures.fake/1234',
          'is_welcomed': False
      }

  def test_get_user_404(self, app):
    with app.test_client() as client:

      rv = client.get('/api/v1/user')
      assert rv.status == '404 NOT FOUND'
      assert rv.json == {'error': 'No signed in user', 'status': 404}

  @patch('rainfall.main.check_csrf', return_value=None)
  @patch('rainfall.main.id_token.verify_oauth2_token')
  def test_login(self, mock_verify, mock_check_csrf, app):
    mock_verify.return_value = {
        'sub': '1234',
        'name': 'Jane Doe',
        'email': 'janedoe@email.fake',
        'picture': 'https://pictures.fake/photo-1234',
    }

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '302 FOUND'
      assert rv.headers['location'] == 'http://localhost:5173/welcome'

      user_id = flask.session['user_id']
      user = db.session.get(User, user_id)
      assert user.google_id == '1234'
      assert user.name == 'Jane Doe'
      assert user.email == 'janedoe@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'

  @patch('rainfall.main.check_csrf', return_value=None)
  @patch('rainfall.main.id_token.verify_oauth2_token')
  def test_login_already_welcomed(self, mock_verify, mock_check_csrf, app,
                                  basic_user):
    mock_verify.return_value = {
        'sub': '1234',
        'name': 'Jane Doe',
        'email': 'janedoe@email.fake',
        'picture': 'https://pictures.fake/photo-1234',
    }

    with app.app_context():
      basic_user.is_welcomed = True
      db.session.add(basic_user)
      db.session.commit()

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '302 FOUND'
      assert rv.headers['location'] == 'http://localhost:5173/sites'

      user_id = flask.session['user_id']
      user = db.session.get(User, user_id)
      assert user.google_id == '1234'
      assert user.name == 'Jane Doe'
      assert user.email == 'janedoe@email.fake'
      assert user.picture_url == 'https://pictures.fake/photo-1234'
      assert user.is_welcomed

  @patch('rainfall.main.check_csrf')
  @patch('rainfall.main.id_token.verify_oauth2_token')
  def test_login_no_csrf(self, mock_verify, mock_check_csrf, app):
    mock_check_csrf.return_value = ({
        'status': 400,
        'error': 'Missing CSRF'
    }, 400)

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '400 BAD REQUEST'
      assert rv.json == {'status': 400, 'error': 'Missing CSRF'}

  @patch('rainfall.main.check_csrf', return_value=None)
  @patch('rainfall.main.id_token.verify_oauth2_token')
  def test_login_no_verify(self, mock_verify, mock_check_csrf, app):
    mock_verify.side_effect = ValueError

    with app.test_client() as client:
      rv = client.post('/api/v1/login')
      assert rv.status == '400 BAD REQUEST'
      assert rv.json == dict(status=400, error='Could not verify token')

  def test_welcome(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/user/welcome')
      assert rv.status == '204 NO CONTENT'

      user = db.session.get(User, BASIC_USER_ID)
      assert user.is_welcomed

  def test_welcome_no_user(self, app, basic_user):
    with app.test_client() as client:
      rv = client.post('/api/v1/user/welcome')
      assert rv.status == '404 NOT FOUND'
      assert rv.json == {'status': 404, 'error': 'No signed in user'}

  def test_create_site(self, app, welcomed_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site', json={'site': {'name': 'Some site'}})
      assert rv.status == '204 NO CONTENT'

    with app.app_context():
      user = db.session.get(User, BASIC_USER_ID)
      sites = user.sites
      assert len(sites) == 1
      assert sites[0].name == 'Some site'

  def test_create_site_no_user(self, app):
    with app.test_client() as client:
      rv = client.post('/api/v1/site', json={'site': {'name': 'Some site'}})
      assert rv.status == '404 NOT FOUND'

  def test_create_site_no_user_in_session(self, app, welcomed_user):
    with app.test_client() as client:
      rv = client.post('/api/v1/site', json={'site': {'name': 'Some site'}})
      assert rv.status == '404 NOT FOUND'

  def test_create_site_no_json(self, app, welcomed_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site')
      assert rv.status == '415 UNSUPPORTED MEDIA TYPE'

  def test_create_site_missing_site(self, app, welcomed_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site', json={'foo': 'bar'})
      assert rv.status == '400 BAD REQUEST'

  def test_create_site_missing_name(self, app, welcomed_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site', json={'site': {}})
      assert rv.status == '400 BAD REQUEST'

  def test_list_sites(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get('/api/v1/site/list')
      data = rv.json
      assert rv.status == '200 OK'
      assert data
      sites = data.get('sites')
      assert sites
      assert len(sites) == 2
      names = [site['name'] for site in sites]
      assert 'Cool Site 1' in names
      assert 'Another Cool Site' in names

  def test_list_sites_no_user(self, app):
    with app.test_client() as client:
      rv = client.get('/api/v1/site/list')
      assert rv.status == '404 NOT FOUND'

  def test_list_sites_no_user_in_session(self, app, welcomed_user):
    with app.test_client() as client:
      rv = client.get('/api/v1/site/list')
      assert rv.status == '404 NOT FOUND'

  def test_list_sites_no_sites(self, app, welcomed_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.get('/api/v1/site/list')
      data = rv.json
      assert rv.status == '200 OK'
      assert data
      sites = data.get('sites')
      assert len(sites) == 0
