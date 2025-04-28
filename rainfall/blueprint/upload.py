import os
from uuid import UUID
import io
import tempfile
import logging

import flask
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from rainfall import object_storage
from rainfall.db import db
from rainfall.decorators import with_current_user, with_validated_release
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.site import delete_file as delete_db_file
from rainfall.site import release_path, secure_filename

upload = flask.Blueprint('upload', __name__)

ALLOWED_SONG_EXTS = [
    '.aiff', '.aif', '.alac', '.flac', '.mp3', '.ogg', '.opus', '.wav'
]
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


def extract_metadata(file):
  try:
    with tempfile.NamedTemporaryFile() as temp_file:
      file.save(temp_file.name)

      metadata = {}
      # For MP3 files, use MP3 directly
      if file.filename.lower().endswith('.mp3'):
        audio = MP3(temp_file.name)
        if audio is None:
          return metadata

        if hasattr(audio, 'tags') and audio.tags is not None:
          id3_tags = {'TIT2': 'title', 'TPE1': 'artist', 'TALB': 'album'}

          for id3_tag, metadata_key in id3_tags.items():
            if id3_tag in audio.tags:
              metadata[metadata_key] = str(audio.tags[id3_tag].text[0])
      else:
        # For other formats, use MutagenFile
        audio = MutagenFile(temp_file.name)
        if audio is None:
          return metadata

        if hasattr(audio, 'tags') and audio.tags is not None:
          generic_tags = {
              'title': 'title',
              'artist': 'artist',
              'album': 'album'
          }

          for tag, metadata_key in generic_tags.items():
            if tag in audio.tags:
              metadata[metadata_key] = str(audio.tags[tag][0])

      return metadata
  except Exception as e:
    raise


def write_files(release, claz, *files):
  for file in files:
    name = secure_filename(file.filename)
    if len(name) > 1024:
      return flask.jsonify(status=400,
                           error=f'File name {name} is too long'), 400

    obj = claz(filename=name)

    if claz == File:
      metadata = extract_metadata(file)
      for key, value in metadata.items():
        setattr(obj, key, value)

    yield obj

    cur_release_path = release_path(flask.current_app.config['DATA_DIR'],
                                    release)
    object_path = os.path.join(cur_release_path, obj.filename)
    object_storage.put_object(object_path, file, file.content_type)


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


@upload.route('file/<file_id>/metadata', methods=['POST'])
@with_current_user
def update_file_metadata(file_id, user):
  try:
    file_id = UUID(file_id)
  except ValueError:
    return flask.jsonify(status=400, error='Invalid file ID format'), 400

  file = File.query.get(file_id)
  if not file:
    return flask.jsonify(status=404, error='File not found'), 404

  # Check if user has access to this file
  if file.release.site.user_id != user.id:
    return flask.jsonify(status=403, error='Not authorized'), 403

  data = flask.request.get_json()
  if not data:
    return flask.jsonify(status=400, error='No data provided'), 400

  # Update metadata fields
  for key, value in data.items():
    if hasattr(file, key):
      setattr(file, key, value)

  db.session.add(file)
  db.session.commit()

  return '', 204
