import os
from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user, with_validated_release
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.site import release_path, rename_release_dir

release = flask.Blueprint('release', __name__)


@release.route('release', methods=['POST'])
@with_current_user
def create_release(user):
  if not user.is_welcomed:
    return flask.jsonify(status=400,
                         error='User has not yet been welcomed'), 400

  data = flask.request.get_json()
  release_data = data.get('release')
  if release_data is None:
    return flask.jsonify(status=400, error='Missing release data'), 400
  if release_data.get('name') is None:
    return flask.jsonify(status=400, error='Release name is required'), 400
  if release_data.get('site_id') is None:
    return flask.jsonify(status=400,
                         error='Creating release requires a site_id'), 400

  site = db.session.get(Site, UUID(release_data['site_id']))
  if site is None:
    return flask.jsonify(
        status=404,
        error='Could not find site with id=%s to create release for' %
        release_data['site_id']), 404

  if site.user.id != user.id:
    return flask.jsonify(
        status=401,
        error='Cannot create release for that site, unauthorized'), 401

  release = Release(**release_data)
  site.releases.append(release)
  db.session.add(site)

  cur_release_path = release_path(flask.current_app.config['DATA_DIR'], release)
  os.makedirs(cur_release_path, exist_ok=True)

  db.session.commit()
  return '', 204


@release.route('release/<release_id>')
@with_current_user
@with_validated_release
def get_release(release, user):
  return flask.jsonify(release.serialize())


@release.route('release/<release_id>/artwork')
@with_current_user
@with_validated_release
def get_release_artwork(release, user):
  if release.artwork is None:
    flask.abort(404)

  path = os.path.join(
      '..', release_path(flask.current_app.config['DATA_DIR'], release))
  return flask.send_from_directory(path, release.artwork.filename)


@release.route('release/<release_id>/description', methods=['POST'])
@with_current_user
@with_validated_release
def update_release_description(release, user):
  data = flask.request.get_json()
  description = data.get('description')
  if description is None:
    return flask.jsonify(status=400, error='Missing description'), 400

  release.description = description
  db.session.add(release)
  db.session.commit()

  return '', 204


@release.route('release/<release_id>/name', methods=['POST'])
@with_current_user
@with_validated_release
def update_release_name(release, user):
  data = flask.request.get_json()
  name = data.get('name')
  if name is None:
    return flask.jsonify(status=400, error='Missing name'), 400

  old_name = release.name
  release.name = name
  db.session.add(release)
  db.session.commit()

  rename_release_dir(flask.current_app.config['DATA_DIR'], release, old_name)

  return '', 204
