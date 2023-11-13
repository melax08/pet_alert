#!/bin/bash

sleep 15
python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn pet_alert.wsgi:application --bind 0:8000 -w 4
