import os
import dj_database_url
import django_heroku
from django.utils.translation import gettext_lazy as _

print("USING WATERLOO SETTINGS")
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True  # Application definition

ALLOWED_HOSTS = [
    "*",
    "localhost",
    "127.0.0.1:8000",
    "psychologie.uni-freiburg.de",
    "cam1.psychologie.uni-freiburg.de",
    "cam.psychologie.uni-freiburg.de",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "block",
    "link",
    "users.apps.UsersConfig",
    "fileprovider",
]
AUTH_USER_MODEL = "users.CustomUser"
IMPORT_EXPORT_USE_TRANSACTIONS = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "fileprovider.middleware.FileProviderMiddleware",
]
ROOT_URLCONF = "cognitiveAffectiveMaps.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "cognitiveAffectiveMaps.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DBNAME"),
        "USER": os.getenv("DBUSER"),
        "PASSWORD": os.getenv("DBPASSWORD"),
        "HOST": os.getenv("DBHOST"),
        "PORT": os.getenv("DBPORT"),
    }
}


# DjangoSecure Requirements -- SET ALL TO FALSE FOR DEV
# Redirect all requests to SSL
SECURE_SSL_REDIRECT = True
# Use HHTP Strict Transport Security
SECURE_HSTS_SECONDS = 68400  # An entire day
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# Prevent Clickjacking
SECURE_FRAME_DENY = True
# Prevent browser from guessing assests
SECURE_CONTENT_TYPE_NOSNIFF = True
# Enable browser XSS security protocols
SECURE_BROWSER_XSS_FILTER = True
# Technically not django-secure, but recommended on their site
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv("EMAIL_HOST")  # 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOGIN_URL = "dashboard"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "loginpage"
django_heroku.settings(locals())
LANGUAGE_CODE = "de"
TIME_ZONE = "Etc/GMT-1"  # UTC+1
USE_I18N = True
SITE_ROOT = os.path.dirname(os.path.realpath(__name__))
LOCALE_PATHS = (os.path.join(SITE_ROOT, "locale"),)
USE_L10N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "carter-cam-bucket"
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "static"
# STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static'),
# ]
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, "media")

django_heroku.settings(locals())
DATABASE_URL = os.getenv("DBWATERLOO")
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
