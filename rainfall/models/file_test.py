import pytest

from rainfall.db import db
from rainfall.models.file import File


class FileTest:

  def test_maybe_rename(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      release = releases_user.sites[0].releases[1]
      file = File(filename='s0_r1_file_0.wav')
      release.files.append(file)

      file.maybe_rename()

      assert file.filename == 's0_r1_file_0_1.wav'
      assert file.original_filename == 's0_r1_file_0.wav'

  def test_maybe_rename_10_times(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      release = releases_user.sites[0].releases[1]
      for _ in range(10):
        file = File(filename='s0_r1_file_0.wav')
        release.files.append(file)

        file.maybe_rename()

      assert file.filename == 's0_r1_file_0_10.wav'
      assert file.original_filename == 's0_r1_file_0_9.wav'

  def test_maybe_rename_not_necessary(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      release = releases_user.sites[0].releases[1]
      file = File(filename='foo.mp3')
      release.files.append(file)

      file.maybe_rename()

      assert file.filename == 'foo.mp3'
      assert file.original_filename is None

  def test_rename_non_original_file(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      release = releases_user.sites[0].releases[1]
      for _ in range(4):
        file = File(filename='s0_r1_file_1.wav')
        release.files.append(file)

        file.maybe_rename()

      file = File(filename='s0_r1_file_1_2.wav')
      release.files.append(file)
      file.maybe_rename()

      assert file.filename == 's0_r1_file_1_5.wav'
      assert file.original_filename == 's0_r1_file_1_4.wav'

  def test_maybe_rename_no_release(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      file = File(filename='some_name.mp3')
      with pytest.raises(ValueError):
        file.maybe_rename()

  def test_maybe_rename_other_file_degen_name(self, app, releases_user):
    with app.app_context():
      db.session.add(releases_user)

      release = releases_user.sites[0].releases[1]
      release.files.append(File(filename='foo_bad_name'))
      file = File(filename='foo_bad_name')
      release.files.append(file)

      with pytest.raises(ValueError):
        file.maybe_rename()
