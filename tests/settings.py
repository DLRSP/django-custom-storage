"""Test settings.

Storage/compressor/AWS configuration is applied by the ``custom_storage`` app from
its own defaults; the project only declares the minimal paths and an
``APP_CONFIG['custom_storage']`` block, mirroring how consumers configure it.
"""

import os

from django.utils.translation import gettext_noop

DEBUG = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SECRET_KEY = "NOTASECRET"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compressor",
    "custom_storage",
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3"}}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [os.path.join(BASE_DIR, "templates")],
    }
]

ROOT_URLCONF = "tests.urls"

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
)

USE_TZ = True
LANGUAGE_CODE = "en"
USE_I18N = True

LANGUAGES = [
    ("en", gettext_noop("English")),
    ("it", gettext_noop("Italian")),
]

# Project-specific paths (stay in the project; not owned by the package).
MEDIA_ROOT = "/var/opt/your_project_name/mediaroot/"
STATIC_ROOT = "/var/cache/your_project_name/staticroot/"

# Common storage config via APP_CONFIG; the package derives STATIC_URL/MEDIA_URL,
# STORAGES, COMPRESS_* and AWS_* defaults from this + custom_storage.defaults.
APP_CONFIG = {
    "custom_storage": {
        "BUCKET_NAME": "your_project_bucket_name",
        "CUSTOM_DOMAIN": "cdn.your_project_bucket_name.com",
    },
}

from custom_storage.conf import apply_storage_defaults  # noqa: E402

apply_storage_defaults(globals())
