custom_storage 0.3.3 (2026-06-27)
=================================

Features
--------

- Add ``APP_CONFIG``-based configuration with sensible package defaults, so projects no longer need to repeat the common storage, compression and AWS settings. Call ``custom_storage.conf.apply_storage_defaults(globals())`` from your ``settings.py`` and supply only the project specifics under ``APP_CONFIG["custom_storage"]`` (``BUCKET_NAME``, ``CUSTOM_DOMAIN``, ``FILE_EXPIRE`` ...). Top-level settings still take precedence, so existing projects keep working unchanged.
- Add a ``private`` storage alias backed by ``PrivateMediaS3Boto3Storage`` for uploads that must not be publicly reachable: private ACL, signed expiring URLs and CDN bypass. The object key prefix and URL lifetime are configurable via ``AWS_S3_PRIVATE_LOCATION`` and ``AWS_S3_PRIVATE_URL_EXPIRE`` (or the matching ``APP_CONFIG`` keys). In local/forced-local mode it falls back to the filesystem.


Bug Fixes
---------

- Fix a ``RuntimeError: Settings already configured`` raised when ``DEBUG`` was true: the local-development overrides now assign settings directly instead of calling ``settings.configure()``.
