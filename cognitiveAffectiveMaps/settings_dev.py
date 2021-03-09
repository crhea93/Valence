"""
Django settings
"""

import dj_database_url

print('Using Development Settings!')

DEBUG = True

DATABASE_URL = 'URL-TO-DEV-DATABASE'
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}

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
