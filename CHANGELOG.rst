custom_storage 0.3.14 (2026-08-21)
==================================

No significant changes.


custom_storage 0.3.13 (2026-08-20)
==================================

No significant changes.


custom_storage 0.3.12 (2026-08-18)
==================================

No significant changes.


custom_storage 0.3.11 (2026-08-15)
==================================

No significant changes.


custom_storage 0.3.10 (2026-08-14)
==================================

No significant changes.


custom_storage 0.3.9 (2026-08-13)
=================================

No significant changes.


custom_storage 0.3.8 (2026-08-12)
=================================

No significant changes.


custom_storage 0.3.7 (2026-08-11)
=================================

Features
--------

- Add env-driven S3 object-write gate (``CUSTOM_STORAGE_ALLOW_S3_WRITES``) with Windows deny-by-default and refuse on save/delete.


custom_storage 0.3.6 (2026-08-11)
=================================

No significant changes.


custom_storage 0.3.4 (2026-06-28)
=================================

Bug Fixes
---------

- Set local ``STATIC_URL``/``MEDIA_URL`` fallbacks in forced-local mode. Previously ``apply_storage_defaults`` only derived these URLs from the CDN domain when serving from S3, so a forced-local run with ``DEBUG`` off (e.g. ``collectstatic --force-local-storage``) left ``MEDIA_URL`` unset and aborted settings import with ``ImproperlyConfigured``, which Django then reported as ``Unknown command: 'collectstatic'``.


custom_storage 0.3.3 (2026-06-27)
=================================

Features
--------

- Add ``APP_CONFIG``-based configuration with sensible package defaults, so projects no longer need to repeat the common storage, compression and AWS settings. Call ``custom_storage.conf.apply_storage_defaults(globals())`` from your ``settings.py`` and supply only the project specifics under ``APP_CONFIG["custom_storage"]`` (``BUCKET_NAME``, ``CUSTOM_DOMAIN``, ``FILE_EXPIRE`` ...). Top-level settings still take precedence, so existing projects keep working unchanged.
- Add a ``private`` storage alias backed by ``PrivateMediaS3Boto3Storage`` for uploads that must not be publicly reachable: private ACL, signed expiring URLs and CDN bypass. The object key prefix and URL lifetime are configurable via ``AWS_S3_PRIVATE_LOCATION`` and ``AWS_S3_PRIVATE_URL_EXPIRE`` (or the matching ``APP_CONFIG`` keys). In local/forced-local mode it falls back to the filesystem.


Bug Fixes
---------

- Fix a ``RuntimeError: Settings already configured`` raised when ``DEBUG`` was true: the local-development overrides now assign settings directly instead of calling ``settings.configure()``.
