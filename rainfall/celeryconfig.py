import os

broker_url = os.environ['REDIS_URL'],
result_backend = os.environ['REDIS_URL']
# Don't use a pool, connect every time. There seems to be an issue with
# connections to Redis getting stale.
broker_pool_limit = None
# Retry forever if Redis is unreachable.
broker_connection_max_retries = None
broker_connection_retry_on_startup = True
