from uuid_extensions import uuid7

from rainfall.conftest import BASIC_USER_ID
from rainfall.db import db
from rainfall.decorators import with_current_site, with_current_user, with_validated_release
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.models.user import User


class DecoratorsTest:

  def test_with_current_user(self, app, basic_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/user')
      @with_current_user
      def method_testing(user):
        assert user.id == BASIC_USER_ID
        return 'test result'

      rv = client.get('/testing/only/path/user')
      assert rv.text == 'test result'

  def test_with_current_user_missing_session(self, app, basic_user):
    with app.test_client() as client:

      @app.route('/testing/only/path/user')
      @with_current_user
      def method_testing(user):
        pass

      rv = client.get('/testing/only/path/user')
      assert rv.status == '401 UNAUTHORIZED', rv.text

  def test_with_current_user_not_exist(self, app):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/user')
      @with_current_user
      def method_testing(user):
        pass

      rv = client.get('/testing/only/path/user')
      assert rv.status == '401 UNAUTHORIZED', rv.text

  def test_with_current_site(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      with app.app_context():
        db.session.add(sites_user)
        site_id = str(sites_user.sites[0].id)

      @app.route('/testing/only/path/<site_id>')
      @with_current_user
      @with_current_site
      def method_testing(site, user):
        assert site.user_id == BASIC_USER_ID
        assert user.id == BASIC_USER_ID
        return 'test result'

      rv = client.get(f'/testing/only/path/{site_id}')
      assert rv.text == 'test result'

  def test_with_current_site_missing_site_id(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/foo_site')
      @with_current_user
      @with_current_site
      def method_testing(site, user):
        pass

      rv = client.get(f'/testing/only/path/foo_site')
      assert rv.status == '500 INTERNAL SERVER ERROR'

  def test_with_current_site_unknown_site(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/<site_id>')
      @with_current_user
      @with_current_site
      def method_testing(site, user):
        pass

      rv = client.get(f'/testing/only/path/{uuid7()}')
      assert rv.status == '404 NOT FOUND'

  def test_with_current_site_user_no_match(self, app, sites_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      with app.app_context():
        user = User(google_id=4567, sites=[Site(name='Site 1')])
        db.session.add(user)
        db.session.flush()
        user_id = user.id
        db.session.commit()
        site_id = str(user.sites[0].id)

      @app.route('/testing/only/path/<site_id>')
      @with_current_user
      @with_current_site
      def method_testing(site, user):
        pass

      rv = client.get(f'/testing/only/path/{site_id}')
      assert rv.status == '403 FORBIDDEN'

  def test_with_validated_release(self, app, releases_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      with app.app_context():
        db.session.add(releases_user)
        release_id = str(releases_user.sites[0].releases[0].id)

      @app.route('/testing/only/path/<release_id>')
      @with_current_user
      @with_validated_release
      def method_testing(release, user):
        assert release.site.user_id == BASIC_USER_ID
        assert user.id == BASIC_USER_ID
        return 'test result'

      rv = client.get(f'/testing/only/path/{release_id}')
      assert rv.status == '200 OK'
      assert rv.text == 'test result'

  def test_with_validated_release_missing_release_id(self, app, releases_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/foo_release')
      @with_current_user
      @with_validated_release
      def method_testing(release, user):
        pass

      rv = client.get(f'/testing/only/path/foo_release')
      assert rv.status == '500 INTERNAL SERVER ERROR'

  def test_with_validated_release_404(self, app, releases_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      @app.route('/testing/only/path/<release_id>')
      @with_current_user
      @with_validated_release
      def method_testing(release, user):
        pass

      rv = client.get(f'/testing/only/path/{uuid7()}')
      assert rv.status == '404 NOT FOUND'

  def test_with_validated_release_user_no_match(self, app, releases_user):
    with app.test_client() as client:
      with client.session_transaction() as sess:
        sess['user_id'] = BASIC_USER_ID

      with app.app_context():
        user = User(
            google_id=4567,
            sites=[Site(name='Site 1', releases=[Release(name='Release 1')])])
        db.session.add(user)
        db.session.flush()
        user_id = user.id
        db.session.commit()
        release_id = str(user.sites[0].releases[0].id)

      @app.route('/testing/only/path/<release_id>')
      @with_current_user
      @with_validated_release
      def method_testing(site, user):
        pass

      rv = client.get(f'/testing/only/path/{release_id}')
      assert rv.status == '403 FORBIDDEN'
