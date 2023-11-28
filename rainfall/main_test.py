from unittest.mock import patch

import flask
import pytest
import uuid

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.models.site import Site
from rainfall.models.user import User


class MainTest:

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
