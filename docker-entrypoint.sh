#!/usr/bin/env sh
set -eu

echo "Running migrations..."
python manage.py migrate --noinput

if [ "${AUTO_CREATE_DEFAULT_USERS:-}" = "1" ] || [ "${AUTO_CREATE_DEFAULT_USERS:-}" = "true" ]; then
  echo "Creating default users (AUTO_CREATE_DEFAULT_USERS enabled)..."
  if [ "${AUTO_SEED_DEMO_CONTENT:-}" = "1" ] || [ "${AUTO_SEED_DEMO_CONTENT:-}" = "true" ]; then
    echo "Auto-seeding demo content (AUTO_SEED_DEMO_CONTENT enabled)..."
    python manage.py create_default_users --update
  else
    python manage.py create_default_users --update --no-seed
  fi
fi

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"

