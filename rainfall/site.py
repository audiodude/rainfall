import os
import shutil
import subprocess
from uuid import UUID

from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.models.site import Site


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


def generate_site(data_dir_path, preview_dir_path, site_id):
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
