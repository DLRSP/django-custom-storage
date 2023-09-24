"""Test's settings"""
import os
from django import VERSION as DJANGO_VERSION
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

# Languages we provide translations for, out of the box.
LANGUAGES = [
    ("de", gettext_noop("German")),
    ("en", gettext_noop("English")),
    ("es", gettext_noop("Spanish")),
    ("fr", gettext_noop("French")),
    ("it", gettext_noop("Italian")),
    ("ja", gettext_noop("Japanese")),
    ("nl", gettext_noop("Dutch")),
    ("ru", gettext_noop("Russian")),
    ("zh-hans", gettext_noop("Simplified Chinese")),
    ("zh-hant", gettext_noop("Traditional Chinese")),
]


# Media files (Uploaded Images, Documents, Video, Audio)
MEDIA_ROOT = '/var/opt/your_project_name/mediaroot/'
# Static files (Fonts, CSS, JavaScript, Icons, Theme's Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/var/cache/your_project_name/staticroot/'

AWS_STORAGE_BUCKET_NAME = 'your_project_bucket_name'
AWS_ACCESS_KEY_ID = 'YOUR_PROJECT_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_PROJECT_AWS_SECRET_ACCESS_KEY'
# ...other setting...

# START - Compress and Upload on S3
import os
import sys
import datetime

# Add option to FORCE_LOCAL_STORAGE
# https://www.mslinn.com/django/1300-django-aws-control.html
if "--force-local-storage" in sys.argv:
    print("AWS datastore disabled; using local storage for assets instead.")
    FORCE_LOCAL_STORAGE = True
    sys.argv.remove("--force-local-storage")
else:
    print("Using AWS datastore for assets.")
    FORCE_LOCAL_STORAGE = False

if DJANGO_VERSION < (4, 2):
    if not FORCE_LOCAL_STORAGE:
        DEFAULT_FILE_STORAGE = 'custom_storage.storage.MediaRootCachedS3Storage'
        if not os.getenv('RUN_COMPRESS', False):
            STATICFILES_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
    else:
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    if not FORCE_LOCAL_STORAGE:
        STORAGES = {
            "default": {"BACKEND": "custom_storage.storage.MediaRootCachedS3Storage"},
        }
    else:
        STORAGES = {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        }
    if not os.getenv('RUN_COMPRESS', False):
        STORAGES.update({
            "staticfiles": {"BACKEND": "custom_storage.storage.StaticRootCachedS3Storage"},
        })

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_ROOT = STATIC_ROOT

AWS_S3_CUSTOM_DOMAIN = f"cdn.{AWS_STORAGE_BUCKET_NAME}.org"

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
AWS_S3_OBJECT_PARAMETERS = {
    'Expires': expires,
    'CacheControl': 'max-age=%d' % (int(two_months.total_seconds()),),
}

COMPRESS_CSS_HASHING_METHOD = None
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    # 'compressor.filters.css_default.CssRelativeFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_OUTPUT_DIR = 'compressed_static'
COMPRESS_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
# END - Compress and Upload on S3
