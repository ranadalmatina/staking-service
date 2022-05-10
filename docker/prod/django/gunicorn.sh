#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


python /app/manage.py collectstatic --noinput
gunicorn ws.wsgi --workers 1 --bind 0.0.0.0:8000 --timeout 120 --chdir=/app
