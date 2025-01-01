import glob
import logging
import os
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
def get_object(client, bucket, path):
  print(path)
  return client.get_object(bucket, path)


@inject_client_and_bucket
def put_object(client, bucket, path, file, content_type):
  content_length = file.seek(0, 2)
  file.seek(0)  # Reset the file pointer to the beginning.
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


@inject_client_and_bucket
def download_file(client, bucket, path, output_path):
  client.fget_object(bucket, path, output_path)


@inject_client_and_bucket
def upload_dir_recursively(client, bucket, path, output_path):
  print('upload recursive, path is:', path)
  assert os.path.isdir(path)
  for local_file in glob.glob(path + '/**'):
    remote_path = os.path.join(output_path, os.path.basename(local_file))
    if not os.path.isfile(local_file):
      upload_dir_recursively(local_file, remote_path)
    else:
      client.fput_object(bucket, remote_path, local_file)
