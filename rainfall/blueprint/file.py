import logging
import os
from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.site import release_path

file = flask.Blueprint('file', __name__)

log = logging.getLogger(__name__)


@file.route('file/<file_id>', methods=['DELETE'])
@with_current_user
def delete_file(file_id, user):
  if not user.is_welcomed:
    return flask.jsonify(status=400,
                         error='User has not yet been welcomed'), 400

  file = db.session.get(File, UUID(file_id))
  if file is None:
    return flask.jsonify(status=404,
                         error='Could not find file with id=%s' % file_id), 404

  site = file.release.site

  if site.user.id != user.id:
    return flask.jsonify(
        status=401,
        error='Cannot delete files for that release, unauthorized'), 401

  cur_release_path = release_path(flask.current_app.config['DATA_DIR'],
                                  file.release)
  file_path = os.path.join(cur_release_path, file.filename)

  try:
    os.remove(file_path)
  except FileNotFoundError:
    log.warning('File already deleted, file id=%s' % file.id)
  except OSError:
    log.exception('Could not delete file id=%s', file.id)
    return flask.jsonify(status=500, error='Could not delete file'), 500

  db.session.delete(file)
  db.session.commit()

  return '', 204
