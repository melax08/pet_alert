#!/bin/bash

sleep 10
celery -A pet_alert worker -l INFO
