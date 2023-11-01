import os
import time
from urllib.parse import urljoin

from google.oauth2 import id_token
from google.auth.transport import requests as goog_requests
import flask

from rainfall.db import db
from rainfall.login import check_csrf, save_or_update_google_user
from rainfall.models.user import User

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
db.init_app(app)

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
RAINFALL_FRONTEND_URL = os.environ['RAINFALL_FRONTEND_URL']


@app.route('/')
def index():
  return 'Hello flask'


@app.route('/api/v1/user')
def get_user():
  user_id = flask.session.get('user_id')
  if user_id is None:
    return flask.jsonify(status=404, error='No signed in user'), 404

  user = db.session.get(User, user_id)
  return flask.jsonify(user)


@app.route('/api/v1/login', methods=['POST'])
def login():
  resp = check_csrf()
  if resp:
    return resp

  token = flask.request.form.get('credential')
  try:
    idinfo = id_token.verify_oauth2_token(token, goog_requests.Request(),
                                          GOOGLE_CLIENT_ID)
  except ValueError:
    return flask.jsonify(status=400, error='Could not verify token')

  user_id = save_or_update_google_user(idinfo)
  flask.session['user_id'] = user_id

  return flask.redirect(urljoin(RAINFALL_FRONTEND_URL, '/welcome'))
