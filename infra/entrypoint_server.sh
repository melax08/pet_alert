#!/bin/bash

sleep 15
poetry run python manage.py migrate --no-input
poetry run python manage.py collectstatic --no-input
poetry run gunicorn server.wsgi --bind 0:8000 --workers 4
