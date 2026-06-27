# Third-Party Packages

django-custom-storage integrates with several third-party packages. This document provides information about these packages and their compatibility.

## Required Dependencies

### Django

**Package**: `Django`
**Version**: >= 3.2
**Purpose**: Django web framework
**Links**:
- [PyPI](https://pypi.org/project/Django/)
- [Documentation](https://docs.djangoproject.com/)
- [GitHub](https://github.com/django/django)

### django-storages

**Package**: `django-storages[s3]`
**Version**: Latest stable
**Purpose**: Collection of custom storage backends for Django, including S3 backend
**Links**:
- [PyPI](https://pypi.org/project/django-storages/)
- [Documentation](https://django-storages.readthedocs.io/)
- [GitHub](https://github.com/jschneier/django-storages)

### django-compressor

**Package**: `django-compressor`
**Version**: Latest stable
**Purpose**: Compresses linked and inline JavaScript or CSS into a single cached file
**Links**:
- [PyPI](https://pypi.org/project/django-compressor/)
- [Documentation](https://django-compressor.readthedocs.io/)
- [GitHub](https://github.com/django-compressor/django-compressor)

**Note**: django-compressor is required for `StaticRootCachedS3Storage` which uses `CompressorFileStorage` as the local storage backend.

### boto3

**Package**: `boto3`
**Version**: Latest stable (installed as dependency of django-storages)
**Purpose**: AWS SDK for Python, used by django-storages for S3 integration
**Links**:
- [PyPI](https://pypi.org/project/boto3/)
- [Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [GitHub](https://github.com/boto/boto3)

## Optional Dependencies

### Testing

These packages are included in the `[testing]` extra:

- **pytest**: Testing framework
- **pytest-django**: Django plugin for pytest
- **coverage**: Code coverage tool
- **codecov**: Code coverage reporting

Install with:
```bash
pip install django-custom-storage[testing]
```

### Linting

These packages are included in the `[linting]` extra:

- **flake8**: Linter
- **pylint**: Code analyzer

Install with:
```bash
pip install django-custom-storage[linting]
```

## Compatibility Matrix

| Package | Version | Django 3.2 | Django 4.2 | Django 5.2 |
|---------|---------|------------|------------|------------|
| django-storages | Latest | ✅ | ✅ | ✅ |
| django-compressor | 4.4+ | ✅ | ✅ | ✅ |
| boto3 | Latest | ✅ | ✅ | ✅ |

## Version Compatibility Notes

### Django 3.2

- Uses `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` settings
- `get_storage_class` is available
- `STORAGES` dictionary is not available by default

### Django 4.2

- Introduces `STORAGES` dictionary
- `DEFAULT_FILE_STORAGE` and `STATICFILES_STORAGE` are deprecated but still work
- `get_storage_class` is available

### Django 5.2

- `get_storage_class` is removed
- Uses `import_string` instead (handled automatically by django-custom-storage)
- `STORAGES` dictionary is the recommended way to configure storage

## django-compressor Compatibility

django-compressor is required for `StaticRootCachedS3Storage`. The storage class uses `CompressorFileStorage` as the local storage backend to:

1. Cache compressed files locally
2. Upload compressed files to S3
3. Allow django-compressor to process files locally before uploading

If you don't use django-compressor, you can still use:
- `MediaRootCachedS3Storage` (uses `FileSystemStorage` locally)
- `PublicMediaS3Boto3Storage` (no local caching)
- `PrivateMediaS3Boto3Storage` (no local caching)

## AWS S3 Compatibility

django-custom-storage works with any S3-compatible storage service, including:

- Amazon S3
- DigitalOcean Spaces
- MinIO
- Backblaze B2
- Any S3-compatible API

Configure using standard django-storages S3 settings.

## Known Issues and Workarounds

### django-compressor with Django 5.2

django-compressor may have compatibility issues with Django 5.2. The storage classes handle this by:

- Using `STORAGES["compressor"]["BACKEND"]` which should be configured properly
- Falling back gracefully if compressor is not available

### boto3 Authentication

boto3 uses AWS credentials. Make sure to configure:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- Or use AWS IAM roles (for EC2/ECS/Lambda)

See [AWS S3 Configuration](../tutorial/settings.md#aws-s3-configuration) for more details.

## Upgrading Dependencies

To upgrade dependencies:

1. Check the latest versions:
   ```bash
   pip list --outdated
   ```

2. Update requirements:
   ```bash
   pip install --upgrade django-storages django-compressor boto3
   ```

3. Run tests to ensure compatibility:
   ```bash
   python runtests.py
   ```

4. Check for deprecation warnings:
   ```bash
   python -W default manage.py check
   ```

## Reporting Compatibility Issues

If you encounter compatibility issues with third-party packages:

1. Check the package's documentation for known issues
2. Check the package's GitHub issues
3. Report the issue in [django-custom-storage issues](https://github.com/DLRSP/django-custom-storage/issues)
4. Include:
   - Package versions
   - Django version
   - Python version
   - Error traceback
   - Steps to reproduce
