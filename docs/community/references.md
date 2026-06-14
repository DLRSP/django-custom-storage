# References

Useful references and resources for django-custom-storage.

## Official Documentation

### Django

- [Django Storage Documentation](https://docs.djangoproject.com/en/stable/topics/files/)
- [Django File Storage API](https://docs.djangoproject.com/en/stable/ref/files/storage/)
- [Django Static Files](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Django STORAGES Setting (Django 4.2+)](https://docs.djangoproject.com/en/stable/ref/settings/#storages)

### django-storages

- [django-storages Documentation](https://django-storages.readthedocs.io/)
- [S3 Backend](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [django-storages GitHub](https://github.com/jschneier/django-storages)

### django-compressor

- [django-compressor Documentation](https://django-compressor.readthedocs.io/)
- [django-compressor GitHub](https://github.com/django-compressor/django-compressor)

### AWS S3

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS S3 Python SDK (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

## Related Projects

### DLRSP Organization

- [django-errors](https://github.com/DLRSP/django-errors) - Django application for handling server errors
- [Example Project](https://github.com/DLRSP/example) - Example Django projects

### Storage Backends

- [django-storages](https://github.com/jschneier/django-storages) - Collection of custom storage backends for Django
- [django-s3-storage](https://github.com/etianen/django-s3-storage) - Django S3 file storage backend

### Compression

- [django-compressor](https://github.com/django-compressor/django-compressor) - Compresses linked and inline JavaScript or CSS into a single cached file
- [django-pipeline](https://github.com/jazzband/django-pipeline) - Asset packaging library for Django

## Tutorials and Guides

### Django Storage

- [Django File Upload Tutorial](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)
- [Custom Storage Backends](https://docs.djangoproject.com/en/stable/howto/custom-file-storage/)

### AWS S3 Integration

- [Django S3 Storage Guide](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/)
- [Setting up S3 with Django](https://realpython.com/storing-django-static-and-media-files-on-amazon-s3/)

### Compression

- [django-compressor Best Practices](https://django-compressor.readthedocs.io/en/latest/usage/)

## Version Compatibility

### Django Versions

- Django 3.2: [Release Notes](https://docs.djangoproject.com/en/3.2/releases/3.2/)
- Django 4.2: [Release Notes](https://docs.djangoproject.com/en/4.2/releases/4.2/)
- Django 5.2: [Release Notes](https://docs.djangoproject.com/en/5.2/releases/5.2/)

### Python Versions

- Python 3.9: [Release Notes](https://www.python.org/downloads/release/python-390/)
- Python 3.10: [Release Notes](https://www.python.org/downloads/release/python-3100/)
- Python 3.11: [Release Notes](https://www.python.org/downloads/release/python-3110/)

## Blog Posts and Articles

### Storage Patterns

- [Django Storage Pattern for Reusable Apps](https://overtag.dk/v2/blog/a-settings-pattern-for-reusable-django-apps/)
- [Django AWS Control](https://www.mslinn.com/django/1300-django-aws-control.html)

## API References

### Django Storage API

- [FileField Storage](https://docs.djangoproject.com/en/stable/ref/models/fields/#filefield)
- [Storage Class](https://docs.djangoproject.com/en/stable/ref/files/storage/#django.core.files.storage.Storage)
- [get_storage_class (deprecated in Django 5.2)](https://docs.djangoproject.com/en/stable/ref/files/storage/#django.core.files.storage.get_storage_class)
- [import_string (Django 5.2+)](https://docs.djangoproject.com/en/stable/ref/utils/#django.utils.module_loading.import_string)

### django-storages API

- [S3Storage](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#storages.backends.s3.S3Storage)
- [S3Boto3Storage](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#storages.backends.s3boto3.S3Boto3Storage)

## Community

### GitHub

- [django-custom-storage Repository](https://github.com/DLRSP/django-custom-storage)
- [Issues](https://github.com/DLRSP/django-custom-storage/issues)
- [Pull Requests](https://github.com/DLRSP/django-custom-storage/pulls)
- [Discussions](https://github.com/DLRSP/django-custom-storage/discussions)

### Support

- [GitHub Issues](https://github.com/DLRSP/django-custom-storage/issues) - For bug reports and feature requests
- [Documentation](https://dlrsp.github.io/django-custom-storage/) - Full documentation

## Standards and Specifications

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Django Coding Style](https://docs.djangoproject.com/en/stable/internals/contributing/writing-code/coding-style/)

## Tools and Utilities

### Development Tools

- [tox](https://tox.readthedocs.io/) - Testing automation tool
- [pytest](https://docs.pytest.org/) - Testing framework
- [pytest-django](https://pytest-django.readthedocs.io/) - Django plugin for pytest
- [black](https://black.readthedocs.io/) - Code formatter
- [isort](https://pycqa.github.io/isort/) - Import sorter
- [flake8](https://flake8.pycqa.org/) - Linter
- [mypy](https://mypy.readthedocs.io/) - Static type checker
- [coverage](https://coverage.readthedocs.io/) - Code coverage tool

### Documentation Tools

- [MkDocs](https://www.mkdocs.org/) - Documentation generator
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - MkDocs theme

## Additional Resources

### AWS Resources

- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [AWS S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

### Performance Optimization

- [Django Performance Optimization](https://docs.djangoproject.com/en/stable/topics/performance/)
- [CDN Best Practices](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
