from unittest.mock import patch
import io
import os

from werkzeug.utils import secure_filename

from rainfall.db import db
from rainfall.conftest import BASIC_USER_ID
from rainfall.main import create_app


class MainTest:

  def test_create_app_no_errors(self):
    create_app()
