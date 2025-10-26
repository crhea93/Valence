"""
Django development settings
Import base settings and override for development
"""

# Import all settings from base settings
from .settings import *

print("Using Development Settings!")

# Override with development specific settings
DEBUG = True

# Use a fixed SECRET_KEY for development (never use in production!)
SECRET_KEY = "django-insecure-dev-key-for-development-only-do-not-use-in-production"

# Override database to use PostgreSQL for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "camdev",
        "USER": "carter",
        "PASSWORD": "ILoveLuci3!",
        "HOST": "localhost",
        "PORT": "",
    }
}

# Don't update from dj_database_url in dev settings
# prod_db = dj_database_url.config(conn_max_age=500)
# DATABASES['default'].update(prod_db)

# DjangoSecure Requirements -- SET ALL TO FALSE FOR DEV
# Redirect all requests to SSL
SECURE_SSL_REDIRECT = False
# Use HHTP Strict Transport Security
SECURE_HSTS_SECONDS = None
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# Prevent Clickjacking
SECURE_FRAME_DENY = False
# Prevent browser from guessing assests
SECURE_CONTENT_TYPE_NOSNIFF = False
# Enable browser XSS security protocols
SECURE_BROWSER_XSS_FILTER = False
# Technically not django-secure, but recommended on their site
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
