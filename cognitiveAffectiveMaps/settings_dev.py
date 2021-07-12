"""
Django settings
"""
import os
import dj_database_url
import django_heroku
print('Using Development Settings!')

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'camdev',
        'USER': 'carter',
        'PASSWORD': 'ILoveLuci3!',
        'HOST': 'localhost',
        'PORT': '',
    }
}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#django_heroku.settings(locals())
# This is new
prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)

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

