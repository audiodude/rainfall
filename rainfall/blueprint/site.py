import os
from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user, with_current_site
from rainfall.models.site import Site
from rainfall.site import site_path, rename_site_dir

site = flask.Blueprint('site', __name__)


@site.route('/site', methods=['POST'])
@with_current_user
def create_site(user):
  if not user.is_welcomed:
    return flask.jsonify(status=400,
                         error='User has not yet been welcomed'), 400

  data = flask.request.get_json()
  if data is None:
    return flask.jsonify(status=400, error='No JSON provided'), 400
  site_data = data.get('site')
  if site_data is None:
    return flask.jsonify(status=400, error='Missing site data'), 400
  if site_data.get('name') is None:
    return flask.jsonify(status=400, error='Site name is required'), 400

  site = Site(**site_data)
  user.sites.append(site)
  db.session.add(user)

  cur_site_path = site_path(flask.current_app.config['DATA_DIR'], site)
  os.makedirs(cur_site_path, exist_ok=True)

  db.session.commit()
  return '', 204


@site.route('/site/list')
@with_current_user
def list_sites(user):
  return flask.jsonify({'sites': [site.serialize() for site in user.sites]})


@site.route('/site/<site_id>')
@with_current_user
@with_current_site
def get_site(site, user):
  return flask.jsonify(site.serialize())


@site.route('/site/<site_id>/name', methods=['POST'])
@with_current_user
@with_current_site
def rename_site(site, user):
  data = flask.request.get_json()
  if data is None:
    return flask.jsonify(status=400, error='No JSON provided'), 400
  new_name = data.get('name')
  if new_name is None:
    return flask.jsonify(status=400, error='Missing name'), 400

  old_name = site.name
  site.name = new_name
  db.session.add(site)
  db.session.commit()

  rename_site_dir(flask.current_app.config['DATA_DIR'], site, old_name)

  return '', 204
