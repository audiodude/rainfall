from minio import Minio


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
