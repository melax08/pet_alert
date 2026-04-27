#!/bin/bash

uv run gunicorn server.wsgi --bind 0:8000 --workers 4
