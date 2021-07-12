import dj_database_url
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DBNAME'),
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASSWORD'),
        'HOST': os.getenv('DBHOST'),
        'PORT': os.getenv('DBPORT'),
    }
}

# This is new
prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)
