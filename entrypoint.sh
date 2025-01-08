#!/bin/bash

if [[ $# -gt 0 ]]; then
    # If we pass a command, run it (for celery workers)
    exec "$@"
else
    # Else default to starting the server
    exec "pipenv run gunicorn --error-logfile - --access-logfile - -b 0.0.0.0 rainfall.main:create_app()"
fi