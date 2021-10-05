"""
Django settings for languk project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from urllib.parse import quote_plus
import raven

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


def get_env_str(k, default):
    return os.environ.get(k, default)


def get_env_int(k, default):
    return int(get_env_str(k, default))


def get_env_str_list(k, default=""):
    if os.environ.get(k) is not None:
        return os.environ.get(k).strip().split(" ")
    return default


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

SECRET_KEY = get_env_str("SECRET_KEY", "ch&wu3*3p3xim$n75itqy#9gqsr-2^aq09vqz2whb-hy396g92")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = get_env_str_list("ALLOWED_HOSTS", [])

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Application definition

INSTALLED_APPS = [
    "django_rq",
    "django_task",
    "home",
    "corpus",
    "search",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "wagtailtinymce",
    "raven.contrib.django.raven_compat",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "languk.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [os.path.join(PROJECT_DIR, "jinja2")],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "jinja2_env.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.menu_processor",
            ],
            "extensions": [
                "jinja2.ext.i18n",
                "jinja2.ext.with_",
                "wagtail.core.jinja2tags.core",
                "wagtail.admin.jinja2tags.userbar",
                "wagtail.images.jinja2tags.images",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "home.context_processors.menu_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "languk.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env_str("DB_NAME", None),
        "USER": get_env_str("DB_USER", None),
        "PASSWORD": get_env_str("DB_PASS", None),
        "HOST": get_env_str("DB_HOST", None),
        "PORT": get_env_str("DB_PORT", 5432),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

# Internationalization
LANGUAGE_CODE = "uk"

gettext = lambda s: s
LANGUAGES = (
    ("uk", gettext("Ukrainian")),
    ("en", gettext("English")),
)

TIME_ZONE = "Europe/Kiev"

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

STATIC_ROOT = get_env_str("STATIC_ROOT", os.path.join(BASE_DIR, "static"))
STATIC_URL = "/static/"

MEDIA_ROOT = get_env_str("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))
MEDIA_URL = "/media/"

LOCALE_PATHS = (os.path.join(BASE_DIR, "languk/locale"),)

CORPORA_EXPORT_PATH = os.path.join(STATIC_ROOT, "data")

# Wagtail settings

WAGTAIL_SITE_NAME = "languk"
WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "hallo": {"WIDGET": "wagtail.wagtailadmin.rich_text.HalloRichTextArea"},
    "default": {"WIDGET": "wagtailtinymce.rich_text.TinyMCERichTextArea"},
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = "https://lang.org.ua"

MONGODB_USERNAME = get_env_str("MONGODB_USERNAME", "")
MONGODB_PASSWORD = get_env_str("MONGODB_PASSWORD", "")
MONGODB_HOSTS = get_env_str_list("MONGODB_HOST", ["localhost:27017"])

if MONGODB_USERNAME:
    hosts = [
        "mongodb://{}:{}@{}".format(quote_plus(MONGODB_USERNAME), quote_plus(MONGODB_PASSWORD), host)
        for host in MONGODB_HOSTS
    ]
else:
    hosts = ["mongodb://{}".format(host) for host in MONGODB_HOSTS]

MONGODB = {
    "default": {
        "NAME": get_env_str("MONGODB_DB", "ubertext"),  # Default database to connect to
        "LOCATION": hosts,
        "authSource": get_env_str("MONGODB_AUTH_DB", "admin"),
    }
}

REDIS_HOST = get_env_str('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_URL = 'redis://%s:%d/0' % (REDIS_HOST, REDIS_PORT)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': REDIS_URL
    },
}

RQ_PREFIX = "languk_"
QUEUE_DEFAULT = RQ_PREFIX + 'default'
CORPUS_EXPORT_PATH = "/tmp"

RQ_QUEUES = {
    QUEUE_DEFAULT: {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 360000,
    }
}

RQ_SHOW_ADMIN_LINK = True

try:
    GIT_VERSION = raven.fetch_git_sha(os.path.abspath(os.path.join(BASE_DIR, "..")))
except raven.exceptions.InvalidGitRepository:
    GIT_VERSION = "undef"
    pass

RAVEN_CONFIG = {
    "dsn": get_env_str("SENTRY_DSN", None),
    "release": get_env_str("VERSION", GIT_VERSION),
}
