from functools import wraps
from uuid import UUID

import flask

from rainfall.db import db
from rainfall.models.site import Site
from rainfall.models.user import User


def with_current_user(f):
  '''
  Retrieves the current user from the session, performs some checks, and then
  calls the underlying handler
  '''

  @wraps(f)
  def wrapped(*args, **kwargs):
    user_id = flask.session.get('user_id')
    if user_id is None:
      return flask.jsonify(status=404, error='No signed in user'), 404

    user = db.session.get(User, user_id)
    if user is None:
      return flask.jsonify(status=404, error='User does not exist'), 404

    value = f(*args, user=user, **kwargs)
    return value

  return wrapped


def with_current_site(f):
  '''Requires the with_current_user decorator above'''

  @wraps(f)
  def wrapped(*args, **kwargs):
    if 'site_id' not in kwargs:
      return flask.jsonify(status=500,
                           error='Wrapper requires site_id kwarg'), 500

    site_id = kwargs.pop('site_id')
    user = kwargs['user']
    site = db.session.get(Site, UUID(site_id))
    if site is None:
      return flask.jsonify(
          status=404, error=f'Could not find a site with id={site_id}'), 404

    if site.user.id != user.id:
      return flask.jsonify(status=401,
                           error='Not authorized for that site'), 401

    value = f(*args, site=site, **kwargs)
    return value

  return wrapped
