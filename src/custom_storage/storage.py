from storages.backends.s3 import S3Storage
from django.conf import settings
from django.utils.module_loading import import_string
from .settings import (
    AWS_S3_STATIC_LOCATION,
    AWS_S3_STATIC_URL,
    AWS_S3_MEDIA_LOCATION,
    AWS_S3_MEDIA_URL,
)

# For Django 5.2+, get_storage_class was removed, use import_string instead
try:
    from django.core.files.storage import get_storage_class
except ImportError:
    # Django 5.2+ compatibility
    def get_storage_class(import_path):
        return import_string(import_path)


class StaticRootCachedS3Storage(S3Storage):
    """
    S3 storage backend that saves the files locally, too.

    The defaults for ``location`` and ``base_url`` are ``AWS_S3_STATIC_LOCATION`` and
    ``AWS_S3_STATIC_URL``.

    The defaults for ``local_storage`` is ``STORAGE['compressor']['BACKENDS']``

    """

    def __init__(
        self, location=None, base_url=None, local_storage=None, *args, **kwargs
    ):
        super(StaticRootCachedS3Storage, self).__init__(*args, **kwargs)
        if location is None:
            self.location = AWS_S3_STATIC_LOCATION
        if base_url is None:
            self.base_url = AWS_S3_STATIC_URL
        if local_storage is None:
            self.local_storage = get_storage_class(
                settings.STORAGES["compressor"]["BACKEND"]
            )()
        # self.location = "static"
        # self.local_storage = get_storage_class("compressor.storage.CompressorFileStorage")()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super(StaticRootCachedS3Storage, self).save(
            name, self.local_storage._open(name)
        )
        return name


class MediaRootCachedS3Storage(S3Storage):
    """
    S3 storage backend that saves the files locally, too.

    The defaults for ``location`` and ``base_url`` are ``AWS_S3_MEDIA_LOCATION`` and
    ``AWS_S3_MEDIA_URL``.

    The defaults for ``local_storage`` is ``STORAGE['local']['BACKENDS']``

    """

    def __init__(
        self, location=None, base_url=None, local_storage=None, *args, **kwargs
    ):
        super(MediaRootCachedS3Storage, self).__init__(*args, **kwargs)
        if location is None:
            self.location = AWS_S3_MEDIA_LOCATION
        if base_url is None:
            self.base_url = AWS_S3_MEDIA_URL
        if local_storage is None:
            self.local_storage = get_storage_class(
                settings.STORAGES["local"]["BACKEND"]
            )()
        # self.location = "media"
        # self.local_storage = get_storage_class("django.core.files.storage.FileSystemStorage")()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super(MediaRootCachedS3Storage, self).save(
            name, self.local_storage._open(name)
        )
        return name

    def delete(self, name):
        self.local_storage.delete(name)
        super(MediaRootCachedS3Storage, self).delete(name)

        # Delete optimized image if exist
        for extension in ("webp", "avif"):
            print(f"{name}.{extension}")
            self.local_storage.delete(f"{name}.{extension}")
            super(MediaRootCachedS3Storage, self).delete(f"{name}.{extension}")


class PublicMediaS3Boto3Storage(S3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaS3Boto3Storage(S3Storage):
    location = "private"
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
