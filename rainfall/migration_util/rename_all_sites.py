import os

import flask
from werkzeug.utils import secure_filename as old_secure_filename

from rainfall.db import db
from rainfall.main import create_app
from rainfall.site import secure_filename
from rainfall.models import Site


def rename_all_sites():
  print('Querying sites...')
  data_dir_path = flask.current_app.config['DATA_DIR']
  for site in Site.query.all():
    old_path = os.path.join(data_dir_path, str(site.user.id),
                            old_secure_filename(site.name))
    new_path = os.path.join(data_dir_path, str(site.user.id),
                            secure_filename(site.name))
    try:
      print(f'renaming {old_path} to {new_path}')
      os.rename(old_path, new_path)
    except FileNotFoundError:
      print('X - File not found, probably already in new format')

    for release in site.releases:
      old_release_path = os.path.join(new_path,
                                      old_secure_filename(release.name))
      new_release_path = os.path.join(new_path, secure_filename(release.name))

      try:
        print(f'-renaming {old_release_path} to {new_release_path}')
        os.rename(old_release_path, new_release_path)
      except FileNotFoundError:
        print('X - File not found, probably already in new format')

      for file in release.files:
        new_name = secure_filename(file.filename)
        old_file_path = os.path.join(new_release_path, file.filename)
        new_file_path = os.path.join(new_release_path, new_name)

        try:
          print(f'--renaming {old_file_path} to {new_file_path}')
          os.rename(old_file_path, new_file_path)
        except FileNotFoundError:
          print('X - File not found, probably already in new format')
        file.filename = new_name
        db.session.add(file)

    db.session.commit()


if __name__ == '__main__':
  print('Running main...')
  app = create_app()
  with app.app_context():
    rename_all_sites()
