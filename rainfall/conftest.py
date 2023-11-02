import os

import pytest

from rainfall.db import db
from rainfall.main import create_app
from rainfall.models.user import User


@pytest.fixture
def app():
  app = create_app()
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
      'SQLALCHEMY_TEST_DATABASE_URI']
  app.config['TESTING'] = True
  db.init_app(app)

  with app.app_context():
    db.create_all()

  yield app

  with app.app_context():
    db.drop_all()
