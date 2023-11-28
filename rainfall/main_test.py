from rainfall.main import create_app


class MainTest:

  def test_create_app_no_errors(self):
    create_app()
