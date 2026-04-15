#!/bin/bash

uv run gunicorn server.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001 -w 2
