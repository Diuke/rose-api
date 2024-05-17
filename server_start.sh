#!/usr/bin/env bash
# server_start.sh

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
python3 manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL
python3 manage.py setup

(gunicorn roseapi.wsgi -w 3 -b 0.0.0.0:8001 -t 90) &
nginx -g "daemon off;"