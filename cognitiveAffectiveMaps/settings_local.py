# Import all settings from base settings
from .settings import *

print("Using Local Settings!")

# Override with local/test specific settings
DEBUG = True

# Use a fixed SECRET_KEY for testing (never use in production!)
SECRET_KEY = (
    "django-insecure-test-key-for-local-development-only-do-not-use-in-production"
)

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

print("Set HTTPS to False")

# Override database to use SQLite for local/testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Don't update from dj_database_url in local settings
# prod_db = dj_database_url.config(conn_max_age=500)
# DATABASES['default'].update(prod_db)
