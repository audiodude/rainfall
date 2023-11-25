import os
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


def generate_site(data_dir_path, preview_dir_path, id_):
  try:
    out = subprocess.run([
        'faircamp', '--catalog-dir',
        catalog_dir(data_dir_path, id_), '--build-dir',
        build_dir(preview_dir_path, id_), '--cache-dir',
        cache_dir(preview_dir_path, id_)
    ],
                         capture_output=True,
                         check=True)
    print(out.stderr)
    print(out.stdout)
  except subprocess.CalledProcessError as e:
    return (False, e.stderr.decode('utf-8'))
  return (True, None)
