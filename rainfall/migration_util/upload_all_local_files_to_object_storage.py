import os
import shutil

import flask
from werkzeug.utils import secure_filename as old_secure_filename

from rainfall import object_storage
from rainfall.db import db
from rainfall.main import create_app
from rainfall.models import Site
from rainfall.site import build_dir, cache_dir, secure_filename, site_path


def upload_local_files():
  print('Querying sites...')
  preview_dir_path = flask.current_app.config['PREVIEW_DIR']
  data_dir_path = flask.current_app.config['DATA_DIR']
  for site in Site.query.all():
    site_dir_path = site_path(data_dir_path, site)
    build_dir_path = build_dir(preview_dir_path, str(site.id))
    cache_dir_path = cache_dir(preview_dir_path, str(site.id))

    try:
      print(f'Uploading site {site_dir_path} to object storage')
      object_storage.upload_dir_recursively(path=site_dir_path,
                                            output_path=site_dir_path)
    except AssertionError:
      print('    X - Directory not found')

    try:
      print(f'Uploading {build_dir_path} to object storage')
      object_storage.upload_dir_recursively(path=build_dir_path,
                                            output_path=build_dir_path)
    except AssertionError:
      print('    X - Directory not found')

    try:
      print(f'Uploading {cache_dir_path} to object storage')
      object_storage.upload_dir_recursively(path=cache_dir_path,
                                            output_path=cache_dir_path)
    except AssertionError:
      print('    X - Directory not found')


if __name__ == '__main__':
  print('Running upload_local_files...')
  app = create_app()
  with app.app_context():
    upload_local_files()