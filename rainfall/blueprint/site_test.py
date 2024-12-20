import os
from unittest.mock import patch

import flask
import pytest
from uuid_extensions import uuid7

from rainfall import object_storage
from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.site import Site
from rainfall.models.user import User
from rainfall.site import site_path


class SiteTest:

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
      assert rv.status == '401 UNAUTHORIZED'

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

  def test_create_site_duplicate_name(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site', json={'site': {'name': 'Cool Site 1'}})
      assert rv.status == '400 BAD REQUEST'
      assert 'error' in rv.json

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
      assert rv.status == '401 UNAUTHORIZED'

  def test_list_sites_no_user_in_session(self, app, welcomed_user):
    with app.test_client() as client:
      rv = client.get('/api/v1/site/list')
      assert rv.status == '401 UNAUTHORIZED'

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

  @patch('rainfall.blueprint.site.rename_site_dir')
  def test_rename_site(self, mock_rename_dir, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(f'/api/v1/site/{site_id}/name',
                       json={'name': 'New Name'})
      assert rv.status == '204 NO CONTENT'

      mock_rename_dir.assert_called_once_with(app.config['DATA_DIR'],
                                              sites_user.sites[0],
                                              'Cool Site 1')

    with app.app_context():
      site = db.session.get(Site, site_id)
      assert site.name == 'New Name'

  def test_rename_site_no_user(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      rv = client.post(f'/api/v1/site/{site_id}/name',
                       json={'name': 'New Name'})
      assert rv.status == '401 UNAUTHORIZED'

  def test_rename_site_no_json(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(f'/api/v1/site/{site_id}/name')
      assert rv.status == '415 UNSUPPORTED MEDIA TYPE'

  def test_rename_site_missing_name(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post('/api/v1/site', json={'name': None})
      assert rv.status == '400 BAD REQUEST'

  def test_rename_site_duplicate_name(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.post(f'/api/v1/site/{site_id}/name',
                       json={'name': 'Another Cool Site'})
      assert rv.status == '400 BAD REQUEST'
      assert 'error' in rv.json

  def test_delete_site(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/site/{site_id}')
      assert rv.status == '204 NO CONTENT', rv.json

      site = db.session.get(Site, site_id)
      assert site is None

  def test_delete_site_no_user(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      rv = client.delete(f'/api/v1/site/{site_id}')
      assert rv.status == '401 UNAUTHORIZED'

  def test_delete_site_no_site(self, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)

      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      rv = client.delete(f'/api/v1/site/{uuid7()}')
      assert rv.status == '404 NOT FOUND'

  @patch('rainfall.blueprint.site.object_storage.rmtree')
  def test_delete_site_filesystem_error(self, mock_rmtree, app, sites_user):
    with app.app_context(), app.test_client() as client:
      db.session.add(sites_user)
      site_id = sites_user.sites[0].id

      object_client = object_storage.connect(app)
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      mock_rmtree.side_effect = Exception('Some error')

      rv = client.delete(f'/api/v1/site/{site_id}')
      assert rv.status == '500 INTERNAL SERVER ERROR'

      site = db.session.get(Site, site_id)
      assert site is not None
