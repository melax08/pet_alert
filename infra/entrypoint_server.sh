#!/bin/bash

sleep 15
uv run python manage.py migrate --no-input
uv run python manage.py collectstatic --no-input
uv run gunicorn server.wsgi --bind 0:8000 --workers 4
