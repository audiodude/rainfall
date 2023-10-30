import flask

app = flask.Flask(__name__)


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

  return flask.redirect('/')
