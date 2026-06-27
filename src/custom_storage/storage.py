from django.conf import settings
from django.utils.module_loading import import_string
from storages.backends.s3 import S3Storage

from . import defaults


# Django deprecated django.core.files.storage.get_storage_class in 4.2 and
# removed it in 5.1. Resolve via import_string so we never trigger the
# deprecation warning (fatal under -W error) nor break on Django 5.1+. Kept as a
# module-level name for backward compatibility.
def get_storage_class(import_path):
    return import_string(import_path)


class StaticRootCachedS3Storage(S3Storage):
    """S3 backend for static assets that also writes them to a local cache.

    Defaults: ``location`` and ``base_url`` from ``AWS_S3_STATIC_LOCATION`` /
    ``AWS_S3_STATIC_URL``; local cache from the ``compressor`` storage alias.
    """

    def __init__(
        self, location=None, base_url=None, local_storage=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if location is None:
            self.location = getattr(
                settings, "AWS_S3_STATIC_LOCATION", defaults.STATIC_LOCATION
            )
        if base_url is None:
            self.base_url = (
                getattr(settings, "AWS_S3_STATIC_URL", None)
                or settings.STATIC_URL
            )
        if local_storage is None:
            self.local_storage = get_storage_class(
                settings.STORAGES["compressor"]["BACKEND"]
            )()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super().save(name, self.local_storage._open(name))
        return name


class MediaRootCachedS3Storage(S3Storage):
    """S3 backend for media that also writes files to a local cache.

    Defaults: ``location`` and ``base_url`` from ``AWS_S3_MEDIA_LOCATION`` /
    ``AWS_S3_MEDIA_URL``; local cache from the ``local`` storage alias.
    """

    def __init__(
        self, location=None, base_url=None, local_storage=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if location is None:
            self.location = getattr(
                settings, "AWS_S3_MEDIA_LOCATION", defaults.MEDIA_LOCATION
            )
        if base_url is None:
            self.base_url = (
                getattr(settings, "AWS_S3_MEDIA_URL", None)
                or settings.MEDIA_URL
            )
        if local_storage is None:
            self.local_storage = get_storage_class(
                settings.STORAGES["local"]["BACKEND"]
            )()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super().save(name, self.local_storage._open(name))
        return name

    def delete(self, name):
        self.local_storage.delete(name)
        super().delete(name)

        # Remove the optimized variants generated alongside the original.
        for extension in ("webp", "avif"):
            self.local_storage.delete(f"{name}.{extension}")
            super().delete(f"{name}.{extension}")


class PublicMediaS3Boto3Storage(S3Storage):
    """Public-read media on S3 (served from the CDN custom domain)."""

    location = defaults.MEDIA_LOCATION
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaS3Boto3Storage(S3Storage):
    """Private media on S3, served through signed, expiring URLs.

    Used for uploads that must not be publicly reachable. ``querystring_auth`` is
    forced on so URLs are signed regardless of the project-wide
    ``AWS_QUERYSTRING_AUTH`` value, and the CDN custom domain is bypassed. The object
    key prefix and signed-URL lifetime are configurable via ``AWS_S3_PRIVATE_LOCATION``
    and ``AWS_S3_PRIVATE_URL_EXPIRE``.
    """

    location = defaults.PRIVATE_LOCATION
    default_acl = "private"
    file_overwrite = False
    custom_domain = False
    querystring_auth = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = getattr(
            settings, "AWS_S3_PRIVATE_LOCATION", defaults.PRIVATE_LOCATION
        )
        self.querystring_expire = int(
            getattr(
                settings,
                "AWS_S3_PRIVATE_URL_EXPIRE",
                defaults.PRIVATE_URL_EXPIRE,
            )
        )
