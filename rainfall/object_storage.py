from minio import Minio
from minio.deleteobjects import DeleteObject


def connect(app):
  return Minio(app.config['MINIO_ENDPOINT'],
               access_key=app.config['MINIO_ACCESS_KEY'],
               secret_key=app.config['MINIO_SECRET_KEY'],
               secure=False)


def create_bucket_if_not_exists(endpoint_url, access_key, secret_key, name):
  client = Minio(endpoint_url,
                 access_key=access_key,
                 secret_key=secret_key,
                 secure=False)
  if not client.bucket_exists(name):
    client.make_bucket(name)


def rmtree(client, bucket, path):
  delete_object_list = map(
      lambda x: DeleteObject(x.object_name),
      client.list_objects(bucket, path, recursive=True),
  )

  # DO NOT SUBMIT: Error handling
  errors = client.remove_objects(bucket, delete_object_list)
  for error in errors:
    print(error)
