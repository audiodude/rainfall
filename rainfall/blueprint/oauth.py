import flask


class OauthBlueprintFactory:

  def __init__(self, oauth_lib):
    self.oauth_lib = oauth_lib

  def get_blueprint(self):
    oauth = flask.Blueprint('oauth', __name__)

    netlify = self.oauth_lib.register(
        name='netlify',
        authorize_url='https://app.netlify.com/authorize',
        authorize_params=None,
        access_token_url='https://api.netlify.com/oauth/token',
        api_base_url='https://api.netlify.com/api/v1/',
    )

    @oauth.route('/oauth/netlify/login')
    def login():
      redirect_uri = flask.url_for('oauth.authorize', _external=True)
      return netlify.authorize_redirect(redirect_uri)

    @oauth.route('/oauth/netlify/authorize')
    def authorize():
      print(flask.request.args.to_dict())
      token = netlify.authorize_access_token()

      # TODO: Add token to database.

      sites = netlify.get('sites', token=token)
      return sites.text

    return oauth
