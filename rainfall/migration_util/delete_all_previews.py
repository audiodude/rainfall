import os
import shutil

import flask
from werkzeug.utils import secure_filename as old_secure_filename

from rainfall.db import db
from rainfall.main import create_app
from rainfall.models import Site
from rainfall.site import build_dir, cache_dir, secure_filename, site_path


def rename_all_sites():
  print('Querying sites...')
  data_dir_path = flask.current_app.config['DATA_DIR']
  preview_dir_path = flask.current_app.config['PREVIEW_DIR']
  for site in Site.query.all():
    site_dir_path = site_path(data_dir_path, site)
    build_dir_path = build_dir(preview_dir_path, str(site.id))
    cache_dir_path = cache_dir(preview_dir_path, str(site.id))
    try:
      print(f'Deleting public dir for site {site_dir_path} -- {build_dir_path}')
      shutil.rmtree(build_dir_path)
      print(f'Deleting cache dir for site {site_dir_path} -- {cache_dir_path}')
      shutil.rmtree(cache_dir_path)
    except FileNotFoundError:
      print('X - File not found, probably already deleted')


if __name__ == '__main__':
  print('Running main...')
  app = create_app()
  with app.app_context():
    rename_all_sites()
