"""Production settings — Railway, PostgreSQL, secure cookies."""
from .base import *
from decouple import config
import dj_database_url

DEBUG = False
SECRET_KEY = config('SECRET_KEY')  # Required in prod, no default
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

# Database — PostgreSQL from DATABASE_URL (Railway provides this)
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files — WhiteNoise (add whitenoise to MIDDLEWARE in base when deploying)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media — ephemeral on Railway, document for later S3
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
