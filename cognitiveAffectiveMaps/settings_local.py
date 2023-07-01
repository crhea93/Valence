import os
import dj_database_url
import django_heroku
print('Using Local Settings!')

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

print('Set HTTPS to False')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}


prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)