import os
import time

from google.oauth2 import id_token
from google.auth.transport import requests as goog_requests
import flask
import jwt
from jwt import PyJWKClient

from rainfall.db import db

app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db.init_app(app)

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']


@app.route('/')
def index():
  return 'Hello flask'


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
  jwks_client = PyJWKClient('https://www.googleapis.com/oauth2/v3/certs')
  signing_key = jwks_client.get_signing_key_from_jwt(token)

  data = jwt.decode(token,
                    signing_key.key,
                    algorithms="RS256",
                    audience=GOOGLE_CLIENT_ID)

  idinfo = id_token.verify_oauth2_token(token, goog_requests.Request(),
                                        GOOGLE_CLIENT_ID)

  print(idinfo['sub'])
  return flask.redirect('/')
