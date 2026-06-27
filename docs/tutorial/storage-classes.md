# Storage Classes

django-custom-storage provides several storage classes that extend Django's storage backends to integrate with AWS S3 and provide local caching.

## Available Storage Classes

### StaticRootCachedS3Storage

S3 storage backend that saves static files both locally and on S3. Uses `CompressorFileStorage` as the local storage backend by default.

**Location**: `custom_storage.storage.StaticRootCachedS3Storage`

**Default Configuration**:
- `location`: `AWS_S3_STATIC_LOCATION` (default: "static")
- `base_url`: `AWS_S3_STATIC_URL` (default: `STATIC_URL`)
- `local_storage`: `STORAGES["compressor"]["BACKEND"]` (default: `compressor.storage.CompressorFileStorage`)

**Usage**:

```python
# In settings.py (Django 4.2+)
STORAGES = {
    "staticfiles": {
        "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
    },
}

# In settings.py (Django < 4.2)
STATICFILES_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
```

**Custom Initialization**:

```python
from custom_storage.storage import StaticRootCachedS3Storage

storage = StaticRootCachedS3Storage(
    location="custom_static",
    base_url="https://cdn.example.com/static/",
    local_storage=CustomLocalStorage(),
)
```

**How It Works**:

1. When `save()` is called, the file is first saved to local storage
2. Then the file is opened from local storage and uploaded to S3
3. Both local and S3 copies are maintained

This ensures that:
- Files are available locally for django-compressor to process
- Files are also stored on S3 for CDN delivery
- If S3 upload fails, the local copy still exists

### MediaRootCachedS3Storage

S3 storage backend that saves media files both locally and on S3. Uses `FileSystemStorage` as the local storage backend by default.

**Location**: `custom_storage.storage.MediaRootCachedS3Storage`

**Default Configuration**:
- `location`: `AWS_S3_MEDIA_LOCATION` (default: "media")
- `base_url`: `AWS_S3_MEDIA_URL` (default: `MEDIA_URL`)
- `local_storage`: `STORAGES["local"]["BACKEND"]` (default: `django.core.files.storage.FileSystemStorage`)

**Usage**:

```python
# In settings.py (Django 4.2+)
STORAGES = {
    "default": {
        "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
    },
}

# In settings.py (Django < 4.2)
DEFAULT_FILE_STORAGE = 'custom_storage.storage.MediaRootCachedS3Storage'
```

**Custom Initialization**:

```python
from custom_storage.storage import MediaRootCachedS3Storage

storage = MediaRootCachedS3Storage(
    location="custom_media",
    base_url="https://cdn.example.com/media/",
    local_storage=CustomLocalStorage(),
)
```

**Special Features**:

The `delete()` method automatically deletes optimized image variants (webp and avif) if they exist:

```python
storage.delete("image.jpg")  # Also deletes "image.jpg.webp" and "image.jpg.avif" if they exist
```

**How It Works**:

1. When `save()` is called, the file is first saved to local storage
2. Then the file is opened from local storage and uploaded to S3
3. Both local and S3 copies are maintained

### PublicMediaS3Boto3Storage

S3 storage backend for public media files. Files are stored with public-read ACL.

**Location**: `custom_storage.storage.PublicMediaS3Boto3Storage`

**Default Configuration**:
- `location`: "media"
- `default_acl`: "public-read"
- `file_overwrite`: `False`

**Usage**:

```python
from custom_storage.storage import PublicMediaS3Boto3Storage

storage = PublicMediaS3Boto3Storage()
```

**Features**:
- Files are publicly accessible
- Does not overwrite existing files
- Suitable for public media files that don't need local caching

### PrivateMediaS3Boto3Storage

S3 storage backend for private media files. Files are stored with private ACL.

**Location**: `custom_storage.storage.PrivateMediaS3Boto3Storage`

**Default Configuration**:
- `location`: "private"
- `default_acl`: "private"
- `file_overwrite`: `False`
- `custom_domain`: `False`

**Usage**:

```python
from custom_storage.storage import PrivateMediaS3Boto3Storage

storage = PrivateMediaS3Boto3Storage()
```

**Features**:
- Files are private and require authentication
- Does not use custom domain (uses AWS S3 URLs)
- Does not overwrite existing files
- Suitable for sensitive media files

## Comparison Table

| Storage Class | Local Cache | S3 Storage | Use Case |
|--------------|-------------|------------|----------|
| `StaticRootCachedS3Storage` | Yes (CompressorFileStorage) | Yes | Static files with compression |
| `MediaRootCachedS3Storage` | Yes (FileSystemStorage) | Yes | Media files with local backup |
| `PublicMediaS3Boto3Storage` | No | Yes | Public media files |
| `PrivateMediaS3Boto3Storage` | No | Yes | Private media files |

## Custom Storage Classes

You can create custom storage classes by inheriting from the provided classes:

```python
from custom_storage.storage import MediaRootCachedS3Storage

class CustomMediaStorage(MediaRootCachedS3Storage):
    """Custom media storage with specific configuration"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom initialization
        self.location = "custom_media"
        self.default_acl = "public-read"
```

## Django Version Compatibility

All storage classes are compatible with Django 3.2, 4.2, and 5.2. The storage classes automatically handle differences between Django versions:

- Django 4.2+: Uses `STORAGES` dictionary
- Django < 4.2: Uses `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE`
- Django 5.2+: Uses `import_string` instead of `get_storage_class`

## Error Handling

All storage classes properly handle errors:

- If local save fails, S3 upload is not attempted
- If S3 upload fails, the local copy is retained
- Errors are propagated up so they can be handled by your application

For detailed error handling scenarios, see the [Error Handling documentation](../tutorial/error-handling.md).
