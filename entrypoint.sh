#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --settings=config.settings_docker

echo "Starting Gunicorn..."
exec gunicorn \
    --workers 3 \
    --timeout 120 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    config.wsgi:application
