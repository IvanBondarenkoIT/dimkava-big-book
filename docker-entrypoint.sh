#!/usr/bin/env sh
set -eu

# Build DATABASE_URL at runtime from POSTGRES_* (not stored in git compose files)
if [ -z "${DATABASE_URL:-}" ] && [ -n "${POSTGRES_PASSWORD:-}" ]; then
  export DATABASE_URL="postgres://${POSTGRES_USER:-dimkava}:${POSTGRES_PASSWORD}@${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-dimkava}"
fi

echo "Running migrations..."
python manage.py migrate --noinput

# Sync HR content from repo YAML into DB (idempotent update_or_create in loaders).
# Set AUTO_LOAD_HR_CONTENT=1 on Railway so new translations deploy without manual SSH.
if [ "${AUTO_LOAD_HR_CONTENT:-}" = "1" ] || [ "${AUTO_LOAD_HR_CONTENT:-}" = "true" ]; then
  echo "Loading HR content from YAML (AUTO_LOAD_HR_CONTENT)..."
  python manage.py load_courses
  python manage.py load_onboarding
  python manage.py load_articles
  python manage.py load_news
  python manage.py load_departments || true
fi

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

