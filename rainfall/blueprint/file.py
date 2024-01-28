import logging
import os
from uuid import UUID

import flask

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.site import release_path, delete_file as delete_db_file

file = flask.Blueprint('file', __name__)

log = logging.getLogger(__name__)


@file.route('file/<file_id>', methods=['DELETE'])
@with_current_user
def delete_file(file_id, user):
  if not user.is_welcomed:
    return flask.jsonify(status=400,
                         error='User has not yet been welcomed'), 400

  return delete_db_file(File, file_id, user)
