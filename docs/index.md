# Quickstart

Django Custom Storage provides custom storage backends for Django that integrate with AWS S3 and django-compressor. It offers S3 storage backends that cache files locally, making it ideal for production environments where you need both cloud storage and local caching.

## Features

- **S3 Storage with Local Caching**: Files are saved to both S3 and local storage
- **Static Files Support**: Specialized storage for static files with compression
- **Media Files Support**: Dedicated storage for media files
- **django-compressor Integration**: Seamless integration with django-compressor
- **Django 3.2+ Support**: Compatible with Django 3.2, 4.2, and 5.2
- **Flexible Configuration**: Easy configuration through Django settings

## Requirements

- Python 3.8 or higher
- Django 3.2 or higher
- django-storages (for S3 backend)
- django-compressor (for static file compression)

## Installation

Install django-custom-storage from PyPI:

```bash
pip install django-custom-storage
```

## Quick Setup

### 1. Add to INSTALLED_APPS

Add `compressor` and `custom_storage` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    "compressor",
    "custom_storage",
    # ... other apps
]
```

### 2. Configure AWS S3 Settings

Add your AWS S3 configuration to `settings.py`:

```python
# AWS S3 Configuration
AWS_STORAGE_BUCKET_PREFIX = "cdn"
AWS_STORAGE_BUCKET_NAME = "your_bucket_name"
AWS_STORAGE_BUCKET_TLD = "com"

AWS_ACCESS_KEY_ID = 'YOUR_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_ACCESS_KEY'
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}"

# File paths
MEDIA_ROOT = '/var/opt/your_project/mediaroot/'
STATIC_ROOT = '/var/cache/your_project/staticroot/'
STATIC_URL = '/static/'
```

### 3. Configure Storage Backends

Configure the storage backends for static and media files:

```python
# For Django 4.2+
STORAGES = {
    "default": {
        "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
    },
    "staticfiles": {
        "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
    },
}

# For Django < 4.2
DEFAULT_FILE_STORAGE = 'custom_storage.storage.MediaRootCachedS3Storage'
STATICFILES_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
```

### 4. Configure django-compressor (Optional)

If you want to use compression:

```python
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
COMPRESS_ROOT = STATIC_ROOT

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
```

That's it! Your Django project is now configured to use custom storage backends with S3 and local caching.

## Storage Classes

django-custom-storage provides several storage classes:

- **StaticRootCachedS3Storage**: For static files with local caching
- **MediaRootCachedS3Storage**: For media files with local caching
- **PublicMediaS3Boto3Storage**: Public media files on S3
- **PrivateMediaS3Boto3Storage**: Private media files on S3

See the [Storage Classes documentation](../tutorial/storage-classes.md) for more details.

## Next Steps

- Read the [Settings documentation](../tutorial/settings.md) for detailed configuration options
- Check out the [Example project](../tutorial/example.md) for a complete implementation
- See [References](../community/references.md) for additional resources
