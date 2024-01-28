import os
from uuid import UUID

import flask
from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.decorators import with_current_user
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.site import release_path

upload = flask.Blueprint('upload', __name__)

ALLOWED_SONG_EXTS = ['.aiff', '.aif', '.flac', '.mp3', '.ogg', '.opus', '.wav']


@upload.route('upload/release/<release_id>/song', methods=['POST'])
@with_current_user
def upload_release_song(release_id, user):

  def allowed_file(filename):
    if '.' not in filename:
      return False
    return '.' + filename.rsplit('.', 1)[1].lower() in ALLOWED_SONG_EXTS

  def check_song_file_types(song_files):
    for f in song_files:
      if not allowed_file(f.filename):
        return flask.jsonify(status=400,
                             error='File %s is not an allowed file type (%s)' %
                             (f.filename, ' '.join(ALLOWED_SONG_EXTS))), 400

  print(release_id)
  release = db.session.get(Release, UUID(release_id))
  site = release.site
  upload_user = site.user

  if upload_user.id != user.id:
    return flask.jsonify(status=401,
                         error='Cannot upload data to that release'), 401

  song_files = flask.request.files.getlist("song[]")
  if not song_files:
    return flask.jsonify(status=400, error='No songs uploaded'), 400

  resp = check_song_file_types(song_files)
  if resp is not None:
    return resp

  cur_release_path = release_path(flask.current_app.config['DATA_DIR'], release)
  os.makedirs(cur_release_path, exist_ok=True)

  for song in song_files:
    name = secure_filename(song.filename)
    if len(name) > 1024:
      return flask.jsonify(status=400,
                           error=f'File name {name} is too long'), 400
    file = File(filename=name)
    release.files.append(file)
    # Give the file a new name if it's a dupe. This must be done after
    # the file is added to the release.
    file.maybe_rename()

    # Write the file to the filesystem.
    song.save(os.path.join(cur_release_path, file.filename))

  db.session.add(release)
  db.session.commit()

  return '', 204
