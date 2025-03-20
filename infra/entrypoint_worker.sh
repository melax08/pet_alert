#!/bin/bash

uv run celery -A server worker -l INFO --concurrency 2
