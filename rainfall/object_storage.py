import logging
from functools import wraps

import flask
from minio import Minio
from minio.deleteobjects import DeleteObject

log = logging.getLogger(__name__)


class ObjectStorageException(Exception):
  pass


class ObjectDeleteException(ObjectStorageException):
  pass


def connect(app=None):
  if app is None:
    app = flask.current_app
  return Minio(app.config['MINIO_ENDPOINT'],
               access_key=app.config['MINIO_ACCESS_KEY'],
               secret_key=app.config['MINIO_SECRET_KEY'],
               secure=False)


def inject_client_and_bucket(fn):

  @wraps(fn)
  def wrapper(*args, **kwargs):
    client = connect()
    bucket = flask.current_app.config['MINIO_BUCKET']
    return fn(client, bucket, *args, **kwargs)

  return wrapper


def create_bucket_if_not_exists(app):
  client = connect(app)
  bucket = app.config['MINIO_BUCKET']
  if not client.bucket_exists(bucket):
    client.make_bucket(bucket)


@inject_client_and_bucket
def put_object(client, bucket, path, file, content_length, content_type):
  '''
  This is a thin wrapper, but is here in case we want to do something
  different in the future.
  '''
  client.put_object(bucket, path, file, content_length, content_type)


@inject_client_and_bucket
def rmtree(client, bucket, path):
  delete_object_list = map(
      lambda x: DeleteObject(x.object_name),
      client.list_objects(bucket, path, recursive=True),
  )

  errors = client.remove_objects(bucket, delete_object_list)
  num_errors = 0
  for e in errors:
    log.error('Error deleting %s: %s', e.object_name, e.error_message)
    num_errors += 1

  if num_errors > 0:
    raise ObjectDeleteException(
        f'Could not delete all objects from {path}, {num_errors} errors (see log)'
    )
