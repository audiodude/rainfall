import os
from uuid import UUID

import flask
from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.decorators import with_current_user, with_validated_release
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.site import delete_file as delete_db_file, release_path

upload = flask.Blueprint('upload', __name__)

ALLOWED_SONG_EXTS = ['.aiff', '.aif', '.flac', '.mp3', '.ogg', '.opus', '.wav']
ALLOWED_ART_EXTS = ['.gif', '.jpg', '.jpeg', '.png', '.webp']


def check_file_types(allowed_exts, *song_files):

  def allowed_file(filename):
    if '.' not in filename:
      return False
    return '.' + filename.rsplit('.', 1)[1].lower() in allowed_exts

  for f in song_files:
    if not allowed_file(f.filename):
      return flask.jsonify(status=400,
                           error='File %s is not an allowed file type (%s)' %
                           (f.filename, ' '.join(allowed_exts))), 400


def write_files(release, claz, *files):
  for song in files:
    name = secure_filename(song.filename)
    if len(name) > 1024:
      return flask.jsonify(status=400,
                           error=f'File name {name} is too long'), 400

    file = claz(filename=name)
    # Yield so that the calling function can properly save file to db.
    yield file

    # Write the file to the filesystem.
    cur_release_path = release_path(flask.current_app.config['DATA_DIR'],
                                    release)
    song.save(os.path.join(cur_release_path, file.filename))


@upload.route('upload/release/<release_id>/song', methods=['POST'])
@with_current_user
@with_validated_release
def upload_release_song(release, user):
  song_files = flask.request.files.getlist("song[]")
  if not song_files:
    return flask.jsonify(status=400, error='No songs uploaded'), 400

  resp = check_file_types(ALLOWED_SONG_EXTS, *song_files)
  if resp is not None:
    return resp

  for file in write_files(release, File, *song_files):
    release.files.append(file)
    # Give the file a new name if it's a dupe. This must be done after
    # the file is added to the release.
    file.maybe_rename()

  db.session.add(release)
  db.session.commit()

  return '', 204


@upload.route('upload/release/<release_id>/art', methods=['POST'])
@with_current_user
@with_validated_release
def upload_release_art(release, user):
  artwork = flask.request.files.get('artwork')
  if not artwork:
    return flask.jsonify(status=400, error='No artwork uploaded'), 400

  resp = check_file_types(ALLOWED_ART_EXTS, artwork)
  if resp is not None:
    return resp

  for artwork in write_files(release, Artwork, artwork):
    if release.artwork is not None:
      delete_db_file(Artwork, str(release.artwork.id), user)
    release.artwork = artwork

  db.session.add(release)
  db.session.commit()

  return '', 204
