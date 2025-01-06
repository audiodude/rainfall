import os

from celery import Celery

task_app = Celery('tasks',
                  broker_url=os.environ['REDIS_URL'],
                  result_backend=os.environ['REDIS_URL'])


@task_app.task
def add(x, y):
  return x + y
