import datetime
import sys
import os
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

logger = logging.getLogger(__name__)

# todo: https://overtag.dk/v2/blog/a-settings-pattern-for-reusable-django-apps/
# todo: https://docs.djangoproject.com/en/5.1/topics/settings/


def setting(name, default=None):
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it will return a default.

    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return getattr(settings, name, default)


# overwrite settings for local DEBUG mode
if settings.DEBUG:
    settings.configure(COMPRESS_ENABLED=False)
    settings.configure(COMPRESS_OFFLINE=False)
    settings.configure(STATIC_URL="/static/")
    settings.configure(COMPRESS_ROOT=settings.STATIC_ROOT)
    settings.configure(COMPRESS_URL=settings.STATIC_URL)

    # todo: check how tow
    # settings.configure(STORAGES=settings.STORAGES["default"]["BACKEND"]("django.contrib.staticfiles.storage.StaticFilesStorage"))
    settings.STORAGES["default"][
        "BACKEND"
    ] = "django.contrib.staticfiles.storage.StaticFilesStorage"
    settings.STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )
    if os.name == "nt":
        MEDIA_ROOT = os.path.join(settings.WORK_DIR, "mediaroot")
        STATIC_ROOT = os.path.join(settings.WORK_DIR, "staticroot")

# STORAGE Configurations
AWS_S3_STATIC_URL = getattr(settings, "AWS_S3_STATIC_URL", settings.STATIC_URL)
if not AWS_S3_STATIC_URL.endswith("/"):
    raise ImproperlyConfigured(
        "The STATIC_URL and AWS_S3_STATIC_URL settings must have a trailing slash."
    )
AWS_S3_STATIC_ROOT = getattr(settings, "AWS_S3_STATIC_ROOT", settings.STATIC_ROOT)
AWS_S3_STATIC_LOCATION = getattr(settings, "AWS_S3_STATIC_LOCATION", "static")

AWS_S3_MEDIA_URL = getattr(settings, "AWS_S3_MEDIA_URL", settings.MEDIA_URL)
if not AWS_S3_MEDIA_URL.endswith("/"):
    raise ImproperlyConfigured(
        "The MEDIA_URL and AWS_S3_MEDIA_URL settings must have a trailing slash."
    )
AWS_S3_MEDIA_ROOT = getattr(settings, "AWS_S3_MEDIA_ROOT", settings.MEDIA_ROOT)
AWS_S3_MEDIA_LOCATION = getattr(settings, "AWS_S3_MEDIA_LOCATION", "media")

AWS_S3_COMPRESS_ROOT = getattr(settings, "AWS_S3_COMPRESS_ROOT", AWS_S3_STATIC_ROOT)
settings.COMPRESS_ROOT = AWS_S3_COMPRESS_ROOT

# Add option to FORCE_LOCAL_STORAGE
# https://www.mslinn.com/django/1300-django-aws-control.html
if "--force-local-storage" in sys.argv:
    # print("AWS datastore disabled; using local storage for assets instead.")
    settings.FORCE_LOCAL_STORAGE = True
    sys.argv.remove("--force-local-storage")
else:
    # print("Using AWS datastore for assets.")
    settings.FORCE_LOCAL_STORAGE = False

# settings.STORAGES = {
#     "default": {
#         "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
#         "OPTIONS": {},
#     },
#     "staticfiles": {
#         "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
#         "OPTIONS": {},
#     },
#     "compressor": {
#         "BACKEND": "compressor.storage.CompressorFileStorage",
#         "OPTIONS": {},
#     },
#     "local": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#         "OPTIONS": {},
#     },
# }

settings.DEFAULT_FILE_STORAGE = setting(
    "DEFAULT_FILE_STORAGE", settings.STORAGES["default"]["BACKEND"]
)
settings.THUMBNAIL_DEFAULT_STORAGE = setting(
    "THUMBNAIL_DEFAULT_STORAGE", settings.DEFAULT_FILE_STORAGE
)

if settings.FORCE_LOCAL_STORAGE:
    settings.STORAGES["default"][
        "BACKEND"
    ] = "django.core.files.storage.FileSystemStorage"
else:
    if os.getenv("RUN_COMPRESS", True):
        settings.STORAGES["staticfiles"][
            "BACKEND"
        ] = "custom_storage.storage.StaticRootCachedS3Storage"

settings.COMPRESS_OUTPUT_DIR = setting("COMPRESS_OUTPUT_DIR", "compressed_static")
settings.COMPRESS_STORAGE = setting(
    "COMPRESS_STORAGE", settings.STORAGES["staticfiles"]["BACKEND"]
)

# AWS S3 Configurations
settings.AWS_S3_FILE_OVERWRITE = setting("AWS_S3_FILE_OVERWRITE", False)
settings.AWS_DEFAULT_ACL = setting("AWS_DEFAULT_ACL", "public-read")
settings.AWS_QUERYSTRING_AUTH = setting("AWS_QUERYSTRING_AUTH", False)
settings.AWS_FILE_EXPIRE = setting("AWS_FILE_EXPIRE", 61)
settings.AWS_PRELOAD_METADATA = setting("AWS_PRELOAD_METADATA", True)

two_months = datetime.timedelta(days=settings.AWS_FILE_EXPIRE)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
settings.AWS_S3_OBJECT_PARAMETERS = setting(
    "AWS_S3_OBJECT_PARAMETERS",
    {
        "Expires": expires,
        "CacheControl": "max-age=%d" % (int(two_months.total_seconds()),),
    },
)

# Compress Configurations
settings.COMPRESS_ENABLED = setting("COMPRESS_ENABLED", True)
settings.COMPRESS_OFFLINE = setting("COMPRESS_OFFLINE", True)
settings.STATICFILES_FINDERS = setting(
    "STATICFILES_FINDERS",
    (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "compressor.finders.CompressorFinder",
    ),
)
settings.COMPRESS_CSS_HASHING_METHOD = setting("COMPRESS_CSS_HASHING_METHOD", None)
settings.COMPRESS_CSS_FILTERS = setting(
    "COMPRESS_CSS_FILTERS",
    [
        "compressor.filters.css_default.CssAbsoluteFilter",
        # 'compressor.filters.css_default.CssRelativeFilter',
        "compressor.filters.cssmin.CSSMinFilter",
    ],
)
settings.COMPRESS_JS_FILTERS = setting(
    "COMPRESS_JS_FILTERS",
    [
        "compressor.filters.jsmin.JSMinFilter",
    ],
)
settings.KEEP_COMMENTS_ON_MINIFYING = setting("KEEP_COMMENTS_ON_MINIFYING", False)
settings.HTML_MINIFY = setting("HTML_MINIFY", True)

# # overwrite settings for local DEBUG mode
# if settings.DEBUG:
#     settings.COMPRESS_ENABLED = False
#     settings.COMPRESS_OFFLINE = False
#     settings.STATIC_URL = "/static/"
#     settings.COMPRESS_ROOT = settings.STATIC_ROOT
#     settings.COMPRESS_URL = settings.STATIC_URL
#     settings.STORAGES["default"][
#         "BACKEND"
#     ] = "django.contrib.staticfiles.storage.StaticFilesStorage"
#     settings.STATICFILES_FINDERS = (
#         "django.contrib.staticfiles.finders.FileSystemFinder",
#         "django.contrib.staticfiles.finders.AppDirectoriesFinder",
#     )
#     if os.name == "nt":
#         MEDIA_ROOT = os.path.join(settings.WORK_DIR, "mediaroot")
#         STATIC_ROOT = os.path.join(settings.WORK_DIR, "staticroot")
