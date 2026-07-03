"""
Default values for the Custom Storage app.

Runtime resolution (Django ``settings`` + optional ``APP_CONFIG['custom_storage']``)
lives in :mod:`custom_storage.conf`. Projects do not need to import this module from
``settings.py``; the values here are applied to ``settings`` during app startup unless
the project already defines the corresponding top-level setting.
"""

from __future__ import annotations

# Storage backend dotted paths.
MEDIA_S3_BACKEND = "custom_storage.storage.MediaRootCachedS3Storage"
STATIC_S3_BACKEND = "custom_storage.storage.StaticRootCachedS3Storage"
PUBLIC_S3_BACKEND = "custom_storage.storage.PublicMediaS3Boto3Storage"
PRIVATE_S3_BACKEND = "custom_storage.storage.PrivateMediaS3Boto3Storage"
STATICFILES_LOCAL_BACKEND = (
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
FILESYSTEM_BACKEND = "django.core.files.storage.FileSystemStorage"
COMPRESSOR_BACKEND = "compressor.storage.CompressorFileStorage"
# STORAGES alias for django-compressor bundle output when COMPRESS_STORAGE is S3.
COMPRESSOR_OUTPUT_ALIAS = "compressor_output"

# S3 object key prefixes.
STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"
# Object key prefix for non-public uploads served through signed, expiring URLs.
PRIVATE_LOCATION = "private"
# Lifetime (seconds) of the signed URLs generated for private uploads.
PRIVATE_URL_EXPIRE = 3600

# CDN custom domain building when only the bucket name is supplied
# (``{PREFIX}.{BUCKET}.{TLD}``). A full ``CUSTOM_DOMAIN`` always wins.
CUSTOM_DOMAIN_PREFIX = "cdn"
CUSTOM_DOMAIN_TLD = "com"

# AWS S3 behaviour.
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False
AWS_FILE_EXPIRE = 61
AWS_PRELOAD_METADATA = True

# django-compressor.
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_OUTPUT_DIR = "compressed_static"
COMPRESS_CSS_HASHING_METHOD = None
COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]
COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.JSMinFilter",
]
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

# HTML minify defaults (consumed by html-minify middlewares when present).
KEEP_COMMENTS_ON_MINIFYING = False
HTML_MINIFY = True

# Mode switches.
FORCE_LOCAL = False
RUN_COMPRESS = False
