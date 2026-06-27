# Settings Configuration

This document describes all the settings available in django-custom-storage.

## Recommended Setup

The package can derive the storage, compression and AWS settings for you from a small
`APP_CONFIG` block plus its built-in defaults. Call `apply_storage_defaults` at the end of
`settings.py`:

```python
APP_CONFIG = {
    "custom_storage": {
        "BUCKET_NAME": "your_bucket_name",
        "CUSTOM_DOMAIN": "cdn.your_bucket_name.com",
    },
}

from custom_storage.conf import apply_storage_defaults

apply_storage_defaults(globals())
```

Any top-level setting you define explicitly takes precedence over the derived value, so the
sections below document both the keys you can override and the values the package fills in.

## Required Settings

### AWS S3 Configuration

These settings are required to use S3 storage:

```python
# AWS S3 Bucket Configuration
AWS_STORAGE_BUCKET_PREFIX = "cdn"  # Prefix for your bucket subdomain
AWS_STORAGE_BUCKET_NAME = "your_bucket_name"  # Your S3 bucket name
AWS_STORAGE_BUCKET_TLD = "com"  # Top-level domain

# AWS Credentials
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
```

The custom domain will be automatically constructed as:
```
{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}
```

Example: `cdn.your_bucket_name.com`

### Storage Backend Configuration

`apply_storage_defaults` populates `STORAGES` for you. Define it explicitly only if you
need to override an alias; the package fills in any alias you leave out:

```python
STORAGES = {
    "default": {
        "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
    },
    "staticfiles": {
        "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
    },
    "compressor": {
        "BACKEND": "compressor.storage.CompressorFileStorage",
    },
    "local": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "private": {
        "BACKEND": "custom_storage.storage.PrivateMediaS3Boto3Storage",
    },
}
```

## Optional Settings

### AWS S3 Custom Domain

```python
AWS_S3_CUSTOM_DOMAIN = (
    f"{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}"
)
```

If not set, it will be automatically constructed from the bucket configuration.

### AWS S3 Static/Media URLs

```python
AWS_S3_STATIC_URL = "https://cdn.example.com/static/"  # Must end with /
AWS_S3_STATIC_LOCATION = "static"  # S3 prefix for static files
AWS_S3_MEDIA_URL = "https://cdn.example.com/media/"  # Must end with /
AWS_S3_MEDIA_LOCATION = "media"  # S3 prefix for media files
```

If not set, defaults to `STATIC_URL` and `MEDIA_URL` respectively.

### AWS S3 Object Parameters

```python
AWS_S3_OBJECT_PARAMETERS = {
    "Expires": "Thu, 31 Dec 2025 20:00:00 GMT",
    "CacheControl": "max-age=94608000",
}
```

These parameters are applied to all uploaded files.

### AWS S3 ACL Settings

```python
AWS_DEFAULT_ACL = "public-read"  # Default ACL for files
AWS_QUERYSTRING_AUTH = False  # Disable query string authentication
AWS_FILE_EXPIRE = 61  # Days until files expire (for cache headers)
AWS_PRELOAD_METADATA = True  # Preload metadata for faster access
AWS_S3_FILE_OVERWRITE = False  # Don't overwrite existing files
```

### django-compressor Settings

```python
COMPRESS_ENABLED = True  # Enable compression
COMPRESS_OFFLINE = True  # Use offline compression
COMPRESS_STORAGE = "custom_storage.storage.StaticRootCachedS3Storage"
COMPRESS_ROOT = STATIC_ROOT  # Root directory for compressed files
COMPRESS_OUTPUT_DIR = "compressed_static"  # Output directory for compressed files

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

COMPRESS_CSS_FILTERS = [
    "compressor.filters.css_default.CssAbsoluteFilter",
    "compressor.filters.cssmin.CSSMinFilter",
]

COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.JSMinFilter",
]

COMPRESS_CSS_HASHING_METHOD = None  # Options: None, 'content', 'mtime'
```

### Local Storage Settings

```python
# File system paths
MEDIA_ROOT = "/var/opt/your_project/mediaroot/"
STATIC_ROOT = "/var/cache/your_project/staticroot/"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
```

### Force Local Storage

To force local storage (useful for development):

```python
# Option 1: Environment variable
import os

FORCE_LOCAL_STORAGE = os.getenv("FORCE_LOCAL_STORAGE", "false").lower() == "true"

# Option 2: Command line argument (deprecated, use environment variable instead)
# if "--force-local-storage" in sys.argv:
#     FORCE_LOCAL_STORAGE = True
```

When `FORCE_LOCAL_STORAGE` is `True`, the storage backends will use local file system storage instead of S3.

## Environment-Specific Settings

### DEBUG Mode

In DEBUG mode, some settings are automatically adjusted:

- `COMPRESS_ENABLED` is set to `False`
- `COMPRESS_OFFLINE` is set to `False`
- `STATIC_URL` is set to `/static/`
- Local storage finders are used instead of compressor finders

### Windows Configuration

On Windows, if `DEBUG=True` and `os.name == "nt"`:

```python
WORK_DIR = os.path.join(settings.BASE_DIR, "work")
MEDIA_ROOT = os.path.join(WORK_DIR, "mediaroot")
STATIC_ROOT = os.path.join(WORK_DIR, "staticroot")
```

## Complete Example

Here's a complete settings configuration example:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ... other Django settings ...

# AWS S3 Configuration
AWS_STORAGE_BUCKET_PREFIX = "cdn"
AWS_STORAGE_BUCKET_NAME = "myproject"
AWS_STORAGE_BUCKET_TLD = "com"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# File paths
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
STATIC_URL = "/static/"

# Force local storage in development
FORCE_LOCAL_STORAGE = os.getenv("FORCE_LOCAL_STORAGE", "false").lower() == "true"

# Storage configuration
if not FORCE_LOCAL_STORAGE:
    STORAGES = {
        "default": {
            "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
        },
        "staticfiles": {
            "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
        },
    }

    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False
    AWS_FILE_EXPIRE = 61
    AWS_PRELOAD_METADATA = True
    AWS_S3_FILE_OVERWRITE = False
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Compression settings
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_STORAGE = "custom_storage.storage.StaticRootCachedS3Storage"
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = "compressed_static"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)
```

## Validation

The following settings are validated at startup:

- `AWS_S3_STATIC_URL` must end with `/`
- `AWS_S3_MEDIA_URL` must end with `/`

If these validations fail, an `ImproperlyConfigured` exception will be raised.
