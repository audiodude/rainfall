import flask
from sqlalchemy import select

from rainfall.db import db
from rainfall.models.user import User


def check_csrf():
  csrf_token_cookie = flask.request.cookies.get('g_csrf_token')
  if not csrf_token_cookie:
    return flask.jsonify(status=400, error='No CSRF token in Cookie'), 400
  csrf_token_body = flask.request.form.get('g_csrf_token')
  if not csrf_token_body:
    return flask.jsonify(status=400, error='No CSRF token in post body'), 400
  if csrf_token_cookie != csrf_token_body:
    return flask.jsonify(status=400,
                         error='Failed to verify double submit cookie'), 400


def save_or_update_google_user(idinfo):
  stmt = select(User).filter_by(google_id=idinfo['sub'])
  user = db.session.execute(stmt).scalar()

  if user is None:
    user = User(google_id=idinfo['sub'])

  user.email = idinfo['email'],
  user.name = idinfo['name'],
  user.picture_url = idinfo['picture']
  db.session.add(user)
  db.session.flush()
  user_id = user.id
  db.session.commit()

  return user_id
