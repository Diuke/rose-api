#!/usr/bin/env bash
# server_start.sh

# Make an __init__.py for the custom processes folder
touch /geoapi/processes/custom_processes/__init__.py

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
python3 manage.py setup

# Start the celery app
celery -A roseapi worker --loglevel=info --detach

# Start the django app at port - use environment variables for workers and timeout.
(gunicorn roseapi.wsgi -w ${WEB_WORKERS:-1} -b 0.0.0.0:8001 -t ${WEB_TIMEOUT:-60}) &
nginx -g "daemon off;"
