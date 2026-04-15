#!/bin/bash

uv run python manage.py migrate --no-input
uv run python manage.py collectstatic --no-input
