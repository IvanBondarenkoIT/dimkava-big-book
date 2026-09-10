FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: gettext for django compilemessages (UI translations .po → .mo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gettext \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

# locale/*/LC_MESSAGES/django.mo are committed; recompile only when .po changes:
# RUN DJANGO_SETTINGS_MODULE=config.settings.base python manage.py compilemessages

ENV PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings.production

# Ensure LF line endings for Linux entrypoint (Windows checkout may use CRLF)
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]

