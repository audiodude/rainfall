from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models.release import Release
from rainfall.models.site import Site

release = flask.Blueprint('release', __name__)


@release.route('release', methods=['POST'])
@with_current_user
def create_release(user):
  if not user.is_welcomed:
    return flask.jsonify(status=400,
                         error='User has not yet been welcomed'), 400

  data = flask.request.get_json()
  if data is None:
    return flask.jsonify(status=400, error='No JSON provided'), 400
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

  site.releases.append(Release(**release_data))
  db.session.add(site)
  db.session.commit()

  return '', 204


@release.route('release/<id_>')
@with_current_user
def get_release(user, id_):
  release = db.session.get(Release, UUID(id_))
  if release is None:
    return flask.jsonify(status=404,
                         error='Could not find release with id=%s' % id_), 404

  if release.site.user.id != user.id:
    return flask.jsonify(status=403,
                         error='Not authorized to load release with id=%s' %
                         id_), 403

  return flask.jsonify(release.serialize())
