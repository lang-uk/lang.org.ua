from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        # Strictly PostgreSQL
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'languk',
        'USER': 'languk-user',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

try:
    from .local import *
except ImportError:
    pass
