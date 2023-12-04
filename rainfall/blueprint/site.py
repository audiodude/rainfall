from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models.site import Site

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

  user.sites.append(Site(**site_data))
  db.session.add(user)
  db.session.commit()

  return '', 204


@site.route('/site/list')
@with_current_user
def list_sites(user):
  return flask.jsonify({'sites': [site.serialize() for site in user.sites]})


@site.route('/site/<id_>')
@with_current_user
def get_site(user, id_):
  site = db.session.get(Site, UUID(id_))
  if site is None:
    return flask.jsonify(status=404, error='Site not found'), 404

  if site.user_id != user.id:
    return flask.jsonify(status=403, error='Cannot access that site'), 403

  return flask.jsonify(site.serialize())
