import os
import time
from uuid import UUID

import flask
from werkzeug.utils import secure_filename

from rainfall.blueprint.user import user as user_blueprint
from rainfall.blueprint.site import site as site_blueprint
from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user
from rainfall.models.file import File
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.models.user import User
from rainfall.site import generate_site, public_dir

ALLOWED_SONG_EXTS = ['.aiff', '.aif', '.flac', '.mp3', '.ogg', '.opus', '.wav']


def allowed_file(filename):
  if '.' not in filename:
    return False
  return '.' + filename.rsplit('.', 1)[1].lower() in ALLOWED_SONG_EXTS


def create_app():
  app = flask.Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
  app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
  app.config['DATA_DIR'] = os.environ['DATA_DIR']
  app.config['PREVIEW_DIR'] = os.environ['PREVIEW_DIR']
  app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max upload
  if os.environ.get('RAINFALL_ENV') != 'test':
    db.init_app(app)

  os.makedirs(app.config['DATA_DIR'], exist_ok=True)
  os.makedirs(app.config['PREVIEW_DIR'], exist_ok=True)

  app.register_blueprint(user_blueprint, url_prefix='/api/v1')
  app.register_blueprint(site_blueprint, url_prefix='/api/v1')

  @app.route('/')
  def index():
    return 'Hello flask'

  @app.route('/api/v1/release', methods=['POST'])
  @with_current_user
  def create_release(user):
    if not user.is_welcomed:
      return flask.jsonify(status=400,
                           error='User has not yet been welcomed'), 400

    data = flask.request.get_json()
    if data is None:
      return flask.jsonify(status=400, error='No JSON provided'), 400
    release_data = data.get('release')
    if release_data is None:
      return flask.jsonify(status=400, error='Missing release data'), 400
    if release_data.get('name') is None:
      return flask.jsonify(status=400, error='Release name is required'), 400
    if release_data.get('site_id') is None:
      return flask.jsonify(status=400,
                           error='Creating release requires a site_id'), 400

    site = db.session.get(Site, UUID(release_data['site_id']))
    if site is None:
      return flask.jsonify(
          status=404,
          error='Could not find site with id=%s to create release for' %
          release_data['site_id']), 404

    site.releases.append(Release(**release_data))
    db.session.add(site)
    db.session.commit()

    return '', 204

  @app.route('/api/v1/upload', methods=['POST'])
  @with_current_user
  def upload(user):
    release_id = flask.request.form.get('release_id')
    if release_id is None:
      return flask.jsonify(status=400, error='No release id given'), 400

    release = db.session.get(Release, UUID(release_id))
    site = release.site
    upload_user = site.user

    if upload_user.id != user.id:
      return flask.jsonify(status=403,
                           error='Cannot upload data to that release'), 403

    song_files = flask.request.files.getlist("song[]")
    if not song_files:
      return flask.jsonify(status=400, error='No songs uploaded'), 400

    for f in song_files:
      if not allowed_file(f.filename):
        return flask.jsonify(status=400,
                             error='File %s is not an allowed file type (%s)' %
                             (f.filename, ' '.join(ALLOWED_SONG_EXTS))), 400

    release_path = os.path.join(app.config['DATA_DIR'], str(user.id),
                                secure_filename(site.name),
                                secure_filename(release.name))
    os.makedirs(release_path, exist_ok=True)
    for song in song_files:
      name = secure_filename(song.filename)
      release.files.append(File(filename=name))
      song.save(os.path.join(release_path, name))

    db.session.add(release)
    db.session.commit()

    return '', 204

  @app.route('/api/v1/preview/<site_id>', methods=['POST'])
  @with_current_user
  @with_current_site
  def create_preview(site, user):
    if len(site.releases) == 0 or not any(f for release in site.releases
                                          for f in release.files):
      return flask.jsonify(
          status=400, error='Cannot preview site without releases/files'), 400

    result = generate_site(app.config['DATA_DIR'], app.config['PREVIEW_DIR'],
                           str(site.id))
    if result[0]:
      return '', 204
    else:
      return flask.jsonify(status=500, error=result[1])

  @app.route('/preview/<site_id>/')
  @with_current_user
  @with_current_site
  def preview_index(site, user):
    return flask.send_from_directory(
        os.path.join('..', app.config['PREVIEW_DIR'], public_dir(site)),
        'index.html')

  @app.route('/preview/<site_id>/<path:filename>')
  @with_current_user
  @with_current_site
  def preview_asset(site, user, filename):
    print(filename)
    if filename.endswith('/'):
      filename += 'index.html'
    return flask.send_from_directory(
        os.path.join('..', app.config['PREVIEW_DIR'], public_dir(site)),
        filename)

  return app
