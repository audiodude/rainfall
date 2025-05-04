import io
import logging
import os
import re
import shutil
import subprocess
import unicodedata
from uuid import UUID

import flask

from rainfall import object_storage
from rainfall.db import db
from rainfall.models.site import Site

log = logging.getLogger(__name__)

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-\\ ]")


def secure_filename(filename):
  filename = unicodedata.normalize("NFKD", filename)
  filename = filename.encode("ascii", "ignore").decode("ascii")

  for sep in os.sep, os.path.altsep:
    if sep:
      filename = filename.replace(sep, "\x41")
  filename = str(
      _filename_ascii_strip_re.sub("", "_".join(
          filename.split('\x41')))).strip("._")

  return filename


def catalog_dir(data_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  return os.path.join(data_dir_path, str(site.user.id),
                      secure_filename(site.name))


def build_dir(preview_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  return os.path.join(preview_dir_path, str(site.user.id),
                      secure_filename(site.name), 'public')


def public_dir(site):
  return os.path.join(str(site.user.id), secure_filename(site.name), 'public')


def cache_dir(preview_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  return os.path.join(preview_dir_path, str(site.user.id),
                      secure_filename(site.name), 'cache')


def site_path(data_dir_path, site, override_name=None):
  name = override_name if override_name else site.name
  return os.path.join(data_dir_path, str(site.user.id), secure_filename(name))


def release_path(data_dir_path, release, override_name=None):
  name = override_name if override_name else release.name
  return os.path.join(site_path(data_dir_path, release.site),
                      secure_filename(name))


def file_path(data_dir_path, file):
  return os.path.join(release_path(data_dir_path, file.release), file.filename)


def site_exists(preview_dir_path, site_id):
  dir_ = build_dir(preview_dir_path, site_id)
  return object_storage.path_exists(dir_, recursive=True)


def download_site_objects(data_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  for release in site.releases:
    for file in release.files:
      path = file_path(data_dir_path, file)
      # The first path is in the object storage, the second is the local path.
      object_storage.download_file(path=path, output_path=path)

    if release.artwork:
      path = file_path(data_dir_path, release.artwork)
      object_storage.download_file(path=path, output_path=path)


def upload_site_objects(preview_dir_path, site_id):
  path = build_dir(preview_dir_path, site_id)
  # The first path is the local path, the second is in object storage.
  object_storage.upload_dir_recursively(path=path, output_path=path)


def generate_eno_files(data_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  for release in site.releases:
    if release.empty():
      continue

    release_eno = flask.render_template(
        'release.eno.jinja2',
        cover_filename=release.artwork.filename if release.artwork else None,
        cover_alt_text='no alt text given' if release.artwork else None,
        description=release.description,
        title=release.name)

    path = release_path(data_dir_path, release)
    os.makedirs(path, exist_ok=True)
    eno_path = os.path.join(path, 'release.eno')
    with open(eno_path, 'w', encoding='utf-8') as f:
      f.write(release_eno)


def cleanup_site(data_dir_path, preview_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  # Delete local cache of data dir, and local cache of preview dir.
  shutil.rmtree(site_path(data_dir_path, site), ignore_errors=True)
  shutil.rmtree(site_path(preview_dir_path, site), ignore_errors=True)


def generate_site(data_dir_path, preview_dir_path, site_id):
  download_site_objects(data_dir_path, site_id)
  generate_eno_files(data_dir_path, site_id)

  # Run faircamp.
  try:
    args = [
        'faircamp', '--catalog-dir',
        catalog_dir(data_dir_path, site_id), '--build-dir',
        build_dir(preview_dir_path, site_id), '--cache-dir',
        cache_dir(preview_dir_path, site_id), '--no-clean-urls'
    ]
    log.info('Running faircamp with args: %s', ' '.join(args))
    output = subprocess.run(args, capture_output=True, check=True, text=True)
    log.debug('Faircamp output:\n===STDOUT===\n%s', output.stdout)

    upload_site_objects(preview_dir_path, site_id)
    generate_and_upload_zip(preview_dir_path, site_id)
  except subprocess.CalledProcessError as e:
    log.exception('Faircamp failed\n===STDOUT===:\n%s', e.output)
    return (False, e.output)
  finally:
    cleanup_site(data_dir_path, preview_dir_path, site_id)

  return (True, None)


def zip_file_path(preview_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  return os.path.join(preview_dir_path, str(site.user.id),
                      secure_filename(site.name))


def generate_and_upload_zip(preview_dir_path, site_id):
  root_dir = zip_file_path(preview_dir_path, site_id)
  out_path = os.path.join(root_dir, 'rainfall_site')
  shutil.make_archive(out_path, 'zip', root_dir=root_dir, base_dir='public')

  zip_path = os.path.join(zip_file_path(preview_dir_path, site_id),
                          'rainfall_site.zip')
  with open(zip_path, 'rb') as f:
    object_storage.put_object(zip_path, f, 'application/zip')


def get_zip_file(preview_dir_path, site):
  zip_path = os.path.join(zip_file_path(preview_dir_path, str(site.id)),
                          'rainfall_site.zip')

  if not object_storage.path_exists(zip_path):
    raise FileNotFoundError(f'Could not find zip file at {zip_path}')

  return object_storage.get_object(zip_path)


def delete_file(clz, file_id, user):
  file = db.session.get(clz, UUID(file_id))
  if file is None:
    return flask.jsonify(status=404, error='File does not exist'), 404

  site = file.release.site

  if site.user.id != user.id:
    return flask.jsonify(
        status=401,
        error='Cannot delete files for that release, unauthorized'), 403

  cur_release_path = release_path(flask.current_app.config['DATA_DIR'],
                                  file.release)
  file_path = os.path.join(cur_release_path, file.filename)

  try:
    object_storage.remove_object(file_path)
  except Exception:
    log.exception('Could not delete file id=%s', file.id)
    return flask.jsonify(status=500, error='Could not delete file'), 500

  db.session.delete(file)
  db.session.commit()

  return '', 204


def rename_release_dir(data_dir_path, release, old_name):
  new_path = release_path(data_dir_path, release)
  if object_storage.path_exists(new_path):
    raise FileExistsError(f'The directory {new_path} already exists')

  old_path = release_path(data_dir_path, release, override_name=old_name)
  object_storage.rename_dir_recursively(old_path, new_path)


def rename_site_dir(data_dir_path, site, old_name):
  new_path = site_path(data_dir_path, site)
  if object_storage.path_exists(new_path):
    raise FileExistsError(f'The directory {new_path} already exists')

  old_path = site_path(data_dir_path, site, override_name=old_name)
  object_storage.rename_dir_recursively(old_path, new_path)
