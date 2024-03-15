import logging
import os
import shutil
import subprocess
from uuid import UUID

import flask
from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.models.site import Site

log = logging.getLogger(__name__)


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


def release_path(data_dir_path, release):
  return os.path.join(data_dir_path, str(release.site.user.id),
                      secure_filename(release.site.name),
                      secure_filename(release.name))


def site_exists(preview_dir_path, site_id):
  dir_ = build_dir(preview_dir_path, site_id)
  return os.path.exists(dir_) and len(os.listdir(dir_)) > 0


def generate_eno_files(data_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  for release in site.releases:
    if release.empty():
      continue

    release_eno = flask.render_template(
        'release.eno.jinja2',
        cover_filename=release.artwork.filename if release.artwork else None,
        cover_alt_text='no alt text given' if release.artwork else None,
        description=release.description)

    eno_path = os.path.join(release_path(data_dir_path, release), 'release.eno')
    with open(eno_path, 'w') as f:
      f.write(release_eno)


def generate_site(data_dir_path, preview_dir_path, site_id):
  generate_eno_files(data_dir_path, site_id)

  try:
    out = subprocess.run([
        'faircamp', '--catalog-dir',
        catalog_dir(data_dir_path, site_id), '--build-dir',
        build_dir(preview_dir_path, site_id), '--cache-dir',
        cache_dir(preview_dir_path, site_id), '--no-clean-urls'
    ],
                         capture_output=True,
                         check=True)
  except subprocess.CalledProcessError as e:
    return (False, e.stderr.decode('utf-8'))
  return (True, None)


def zip_file_path(preview_dir_path, site_id):
  site = db.session.get(Site, UUID(site_id))
  return os.path.join(preview_dir_path, str(site.user.id),
                      secure_filename(site.name))


def generate_zip(preview_dir_path, site_id):
  root_dir = zip_file_path(preview_dir_path, site_id)
  out_path = os.path.join(root_dir, 'rainfall_site')
  shutil.make_archive(out_path, 'zip', root_dir=root_dir, base_dir='public')


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
    os.remove(file_path)
  except FileNotFoundError:
    log.warning('File already deleted, file id=%s' % file.id)
  except OSError:
    log.exception('Could not delete file id=%s', file.id)
    return flask.jsonify(status=500, error='Could not delete file'), 500

  db.session.delete(file)
  db.session.commit()

  return '', 204
