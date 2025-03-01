#!/bin/bash

poetry run celery -A server worker -l INFO --concurrency 2
