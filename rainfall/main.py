import logging
import os

from authlib.integrations.flask_client import OAuth
import flask
from flask_seasurf import SeaSurf

from rainfall.blueprint.file import file as file_blueprint
from rainfall.blueprint.oauth import OauthBlueprintFactory
from rainfall.blueprint.release import release as release_blueprint
from rainfall.blueprint.site import site as site_blueprint
from rainfall.blueprint.upload import upload as upload_blueprint
from rainfall.blueprint.user import UserBlueprintFactory
from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user
from rainfall.site import generate_site, generate_zip, public_dir, site_exists, zip_file_path
from rainfall.test_constants import TEST_FILE_PATH

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


def create_app():
  app = flask.Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
  app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
  app.config['GOOGLE_CLIENT_ID'] = os.environ['GOOGLE_CLIENT_ID']
  app.config['RAINFALL_FRONTEND_URL'] = os.environ['RAINFALL_FRONTEND_URL']
  app.config['MASTODON_APP_NAME'] = os.environ['MASTODON_APP_NAME']
  app.config['MASTODON_REDIRECT_URL'] = os.environ['MASTODON_REDIRECT_URL']
  app.config['MASTODON_WEBSITE'] = os.environ['MASTODON_WEBSITE']
  app.config['DATA_DIR'] = os.environ['DATA_DIR']
  app.config['PREVIEW_DIR'] = os.environ['PREVIEW_DIR']

  # Authlib automatically extracts these
  app.config['NETLIFY_CLIENT_ID'] = os.environ['NETLIFY_CLIENT_ID']
  app.config['NETLIFY_CLIENT_SECRET'] = os.environ['NETLIFY_CLIENT_SECRET']

  app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max upload
  if os.environ.get('RAINFALL_ENV') != 'test':
    db.init_app(app)
  else:
    app.config['TESTING'] = True
    app.config['DATA_DIR'] = os.path.join(TEST_FILE_PATH,
                                          app.config['DATA_DIR'])
    app.config['PREVIEW_DATA'] = os.path.join(TEST_FILE_PATH,
                                              app.config['DATA_DIR'])
  csrf = SeaSurf(app)
  oauth = OAuth(app)

  os.makedirs(app.config['DATA_DIR'], exist_ok=True)
  os.makedirs(app.config['PREVIEW_DIR'], exist_ok=True)

  app.register_blueprint(UserBlueprintFactory(csrf).get_blueprint(),
                         url_prefix='/api/v1')
  app.register_blueprint(OauthBlueprintFactory(oauth).get_blueprint(),
                         url_prefix='/api/v1')
  app.register_blueprint(site_blueprint, url_prefix='/api/v1')
  app.register_blueprint(release_blueprint, url_prefix='/api/v1')
  app.register_blueprint(file_blueprint, url_prefix='/api/v1')
  app.register_blueprint(upload_blueprint, url_prefix='/api/v1')

  FRONTEND_DIR = '../rainfall-frontend/dist'

  @app.route('/api/v1/preview/<site_id>', methods=['GET', 'POST'])
  @with_current_user
  @with_current_site
  def create_preview(site, user):
    if len(site.releases) == 0 or not any(f for release in site.releases
                                          for f in release.files):
      return flask.jsonify(
          status=400, error='Cannot preview site without releases/files'), 400

    if flask.request.method == 'GET':
      if site_exists(app.config['PREVIEW_DIR'], str(site.id)):
        return '', 204
      else:
        return '', 404

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
    # The decorators ensure that the site belongs to the user.
    return flask.send_from_directory(
        os.path.join('..', app.config['PREVIEW_DIR'], public_dir(site)),
        'index.html')

  @app.route('/preview/<site_id>/<path:filename>')
  @with_current_user
  @with_current_site
  def preview_asset(site, user, filename):
    # The decorators ensure that the site belongs to the user.
    if filename.endswith('/'):
      filename += 'index.html'
    return flask.send_from_directory(
        os.path.join('..', app.config['PREVIEW_DIR'], public_dir(site)),
        filename)

  @app.route('/api/v1/zip/<site_id>')
  @with_current_user
  @with_current_site
  def zip(site, user):
    generate_zip(app.config['PREVIEW_DIR'], str(site.id))
    zip_path = zip_file_path(app.config['PREVIEW_DIR'], str(site.id))
    return flask.send_from_directory(os.path.join('..', zip_path),
                                     'rainfall_site.zip')

  @app.route('/')
  @app.route('/<path:filename>')
  def index(filename=None):
    return flask.send_from_directory(FRONTEND_DIR, 'index.html')

  @app.route('/favicon.ico')
  def favicon():
    return flask.send_from_directory(FRONTEND_DIR, 'favicon.ico')

  @app.route('/rainfall_preview.png')
  def rainfall_preview():
    return flask.send_from_directory(FRONTEND_DIR, 'rainfall_preview.png')

  @app.route('/src/<path:filename>')
  def srcs(filename=None):
    return flask.send_from_directory(os.path.join(FRONTEND_DIR, 'src'),
                                     filename)

  @app.route('/assets/<path:filename>')
  def assets(filename=None):
    return flask.send_from_directory(os.path.join(FRONTEND_DIR, 'assets'),
                                     filename)

  return app
