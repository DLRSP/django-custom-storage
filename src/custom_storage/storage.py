from django.core.files.storage import get_storage_class
from storages.backends.s3 import S3Storage


class StaticRootCachedS3Storage(S3Storage):
    """
    S3 storage backend that saves the files locally, too.
    """

    def __init__(self, *args, **kwargs):
        super(StaticRootCachedS3Storage, self).__init__(*args, **kwargs)
        self.location = "static"
        self.local_storage = get_storage_class("compressor.storage.CompressorFileStorage")()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super(StaticRootCachedS3Storage, self).save(name, self.local_storage._open(name))
        return name


class MediaRootCachedS3Storage(S3Storage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(MediaRootCachedS3Storage, self).__init__(*args, **kwargs)
        self.location = "media"
        self.local_storage = get_storage_class("django.core.files.storage.FileSystemStorage")()

    def save(self, name, content, max_length=None):
        self.local_storage._save(name, content)
        super(MediaRootCachedS3Storage, self).save(name, self.local_storage._open(name))
        return name

    def delete(self, name):
        self.local_storage.delete(name)
        super(MediaRootCachedS3Storage, self).delete(name)

        # Delete optimized image if exist
        for extension in ("webp", "avif"):
            self.local_storage.delete(f"{name}.{extension}")
            super(MediaRootCachedS3Storage, self).delete(f"{name}.{extension}")
