from minio import Minio


def create_bucket_if_not_exists(endpoint_url, access_key, secret_key, name):
  client = Minio(endpoint_url,
                 access_key=access_key,
                 secret_key=secret_key,
                 secure=False)
  if not client.bucket_exists(name):
    client.make_bucket(name)
