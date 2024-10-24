from werkzeug.utils import secure_filename as old_secure_filename

from rainfall.main import create_app
from rainfall.site import secure_filename
from rainfall.models import Site


def rename_all_sites():
  for site in Site.query.all():
    old_path = os.path.join(data_dir_path, str(site.user.id),
                            old_secure_filename(name))
    new_path = os.path.join(data_dir_path, str(site.user.id),
                            secure_filename(name))
    print(f'renaming {old_path} to {new_path}')
    os.rename(old_path, new_path)

    for release in site.releases:
      old_release_path = os.path.join(new_path,
                                      old_secure_filename(release.name))
      new_release_path = os.path.join(new_path, secure_filename(release.name))
      print(f'-renaming {old_release_path} to {new_release_path}')
      os.rename(old_release_path, new_release_path)

      for file in release.files:
        new_name = secure_filename(file.filename)
        old_file_path = os.path.join(new_release_path, file.filename)
        new_file_path = os.path.join(new_release_path, new_name)

        print(f'--renaming {old_file_path} to {new_file_path}')
        os.rename(old_file_path, new_file_path)
        file.filename = new_name

  if __name__ == '__main__':
    app = create_app()
    with app.app_context():
      rename_all_sites()
