"""Production settings — PostgreSQL, reverse proxy, secure cookies."""
from .base import *
from decouple import config
import dj_database_url

DEBUG = False
SECRET_KEY = config('SECRET_KEY')  # Required in prod, no default
ALLOWED_HOSTS = [h.strip() for h in config('ALLOWED_HOSTS', default='').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in config('CSRF_TRUSTED_ORIGINS', default='').split(',') if o.strip()]

# Database — PostgreSQL from DATABASE_URL
# Self-hosted Docker Postgres: DATABASE_SSL_REQUIRE=false
# Managed cloud DB (Railway, etc.): DATABASE_SSL_REQUIRE=true
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=config('DATABASE_SSL_REQUIRE', default=False, cast=bool),
    )
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Allow toggling during initial platform bring-up to avoid redirect loops.
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

# Common reverse-proxy setup (Railway/Render/Fly/Nginx): trust X-Forwarded-Proto for https detection.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Static files — WhiteNoise (add whitenoise to MIDDLEWARE in base when deploying)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media — ephemeral on Railway, document for later S3
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
