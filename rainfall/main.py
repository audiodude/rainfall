import os
import time
from urllib.parse import urljoin

from google.oauth2 import id_token
from google.auth.transport import requests as goog_requests
import flask
import jwt
import sqlalchemy
from sqlalchemy import select

from rainfall.db import db
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
  csrf_token_cookie = flask.request.cookies.get('g_csrf_token')
  if not csrf_token_cookie:
    return flask.jsonify(status=400, error='No CSRF token in Cookie.'), 400
  csrf_token_body = flask.request.form.get('g_csrf_token')
  if not csrf_token_body:
    return flask.jsonify(status=400, error='No CSRF token in post body.'), 400
  if csrf_token_cookie != csrf_token_body:
    return flask.jsonify(status=400,
                         error='Failed to verify double submit cookie.'), 400

  token = flask.request.form.get('credential')
  try:
    jwks_client = jwt.PyJWKClient('https://www.googleapis.com/oauth2/v3/certs')
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    data = jwt.decode(token,
                      signing_key.key,
                      algorithms="RS256",
                      audience=GOOGLE_CLIENT_ID)
  except jwt.exceptions.PyJWTError:
    return flask.jsonify(status=400, error='Could not decrypt credential')

  try:
    idinfo = id_token.verify_oauth2_token(token, goog_requests.Request(),
                                          GOOGLE_CLIENT_ID)
  except ValueError:
    return flask.jsonify(status=400, error='Could not verify token')

  stmt = select(User).filter_by(google_id=idinfo['sub'])
  user = db.session.execute(stmt).scalar_one()

  if user is None:
    user = User(google_id=idinfo['sub'])

  user.email = idinfo['email'],
  user.name = idinfo['name'],
  user.picture_url = idinfo['picture']
  db.session.add(user)
  db.session.flush()
  user_id = user.id
  db.session.commit()

  flask.session['user_id'] = user_id

  return flask.redirect(urljoin(RAINFALL_FRONTEND_URL, '/welcome'))
