#!/bin/bash
set -e

./wait-for-db.sh

echo "Running migrations..."
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:80 app:app --log-level info --timeout 3600
