"""
Resolved Custom Storage configuration.

Priority for each value:

1. Top-level Django setting (e.g. ``AWS_DEFAULT_ACL``), if defined and non-empty
   for strings.
2. Nested value inside ``settings.APP_CONFIG["custom_storage"]`` (short keys such
   as ``BUCKET_NAME``, ``CUSTOM_DOMAIN``, ``FILE_EXPIRE``, ``DEFAULT_ACL``).
3. Package defaults from :mod:`custom_storage.defaults`.

This app writes the resolved values onto the project settings because the readers
are external libraries (S3 storage, asset compression, thumbnailing and Django
staticfiles) that read plain ``settings.*``. Some of those libraries read their
settings at ``apps.populate`` time, *before* any ``AppConfig.ready`` runs. The
recommended entry point is therefore to call :func:`apply_storage_defaults` from the
project ``settings.py`` at load time::

    APP_CONFIG = {"custom_storage": {"BUCKET_NAME": "example", "CUSTOM_DOMAIN": "cdn.example.eu"}}
    from custom_storage.conf import apply_storage_defaults
    apply_storage_defaults(globals())

It also runs from :meth:`custom_storage.apps.CustomStorageConfig.ready` for backward
compatibility with projects that still declare every storage setting themselves
(there it is a no-op because every value is already defined).

:func:`apply_storage_defaults` accepts either a settings module namespace (the ``dict``
returned by ``globals()``) or the ``django.conf.settings`` object, and never overwrites
a value the project already defines, except for the local-development overrides applied
when ``DEBUG`` is true (compression off, local static serving).
"""

from __future__ import annotations

import datetime
import os
import sys
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from . import defaults

_UNSET = object()
APP_KEY = "custom_storage"


def setting(name, default=None):
    """Return a Django setting by name, or ``default`` if it is not defined."""
    from django.conf import settings

    return getattr(settings, name, default)


# --- namespace accessors (work on a dict from globals() or a settings object) ---
def _has(ns, name: str) -> bool:
    if isinstance(ns, dict):
        return name in ns
    return hasattr(ns, name)


def _get(ns, name: str, default=_UNSET):
    if isinstance(ns, dict):
        return ns.get(name, default)
    return getattr(ns, name, default)


def _set(ns, name: str, value) -> None:
    if isinstance(ns, dict):
        ns[name] = value
    else:
        setattr(ns, name, value)


def _setdefault(ns, name: str, value) -> None:
    if not _has(ns, name):
        _set(ns, name, value)


def _app_config(ns) -> dict[str, Any]:
    cfg = _get(ns, "APP_CONFIG", None) or {}
    block = cfg.get(APP_KEY) if isinstance(cfg, dict) else None
    return dict(block) if isinstance(block, dict) else {}


def _nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def resolve(ns, django_name: str, nested_key: str, fallback):
    """Top-level (non-empty) > ``APP_CONFIG['custom_storage'][nested_key]`` > fallback."""
    value = _get(ns, django_name, _UNSET)
    if value is not _UNSET and _nonempty(value):
        return value
    nested = _app_config(ns).get(nested_key, _UNSET)
    if nested is not _UNSET and _nonempty(nested):
        return nested
    return fallback


def resolve_bool(ns, django_name: str, nested_key: str, fallback) -> bool:
    """Like :func:`resolve` but an explicit top-level/APP_CONFIG ``False`` wins."""
    if _has(ns, django_name):
        return bool(_get(ns, django_name))
    nested = _app_config(ns)
    if nested_key in nested and nested[nested_key] is not None:
        return bool(nested[nested_key])
    return bool(fallback)


def get_custom_domain(ns) -> str:
    domain = resolve(ns, "AWS_S3_CUSTOM_DOMAIN", "CUSTOM_DOMAIN", "")
    if domain:
        return str(domain)
    bucket = resolve(ns, "AWS_STORAGE_BUCKET_NAME", "BUCKET_NAME", "")
    if bucket:
        prefix = resolve(
            ns,
            "AWS_STORAGE_BUCKET_PREFIX",
            "CUSTOM_DOMAIN_PREFIX",
            defaults.CUSTOM_DOMAIN_PREFIX,
        )
        tld = resolve(
            ns,
            "AWS_STORAGE_BUCKET_TLD",
            "CUSTOM_DOMAIN_TLD",
            defaults.CUSTOM_DOMAIN_TLD,
        )
        return f"{prefix}.{bucket}.{tld}"
    return ""


def get_force_local(ns) -> bool:
    if "--force-local-storage" in sys.argv:
        sys.argv.remove("--force-local-storage")
        return True
    return resolve_bool(
        ns, "FORCE_LOCAL_STORAGE", "FORCE_LOCAL", defaults.FORCE_LOCAL
    )


_FALSEY = frozenset({"", "0", "false", "no", "off"})


def get_run_compress(ns) -> bool:
    env = os.getenv("RUN_COMPRESS")
    if env is not None:
        return env.strip().lower() not in _FALSEY
    return resolve_bool(
        ns, "RUN_COMPRESS", "RUN_COMPRESS", defaults.RUN_COMPRESS
    )


def _object_parameters(ns, file_expire: int) -> dict[str, Any]:
    delta = datetime.timedelta(days=file_expire)
    expires = (datetime.date.today() + delta).strftime(
        "%A, %d %B %Y 20:00:00 GMT"
    )
    computed = {
        "Expires": expires,
        "CacheControl": "max-age=%d" % (int(delta.total_seconds()),),
    }
    top = _get(ns, "AWS_S3_OBJECT_PARAMETERS", _UNSET)
    if top is not _UNSET and top is not None:
        return top
    nested = _app_config(ns).get("OBJECT_PARAMETERS")
    if isinstance(nested, dict):
        merged = dict(computed)
        merged.update(nested)
        return merged
    return computed


def apply_storage_defaults(ns) -> dict[str, Any]:
    """Inject the common storage/compressor/AWS defaults onto ``ns``.

    ``ns`` is a project ``settings.py`` namespace (``globals()``) or the
    ``django.conf.settings`` object. Idempotent and non-destructive: any value the
    project already defines is kept. Returns the resolved S3 location/url/root values.
    """
    force_local = get_force_local(ns)
    run_compress = get_run_compress(ns)
    custom_domain = get_custom_domain(ns)
    static_location = resolve(
        ns,
        "AWS_S3_STATIC_LOCATION",
        "STATIC_LOCATION",
        defaults.STATIC_LOCATION,
    )
    media_location = resolve(
        ns, "AWS_S3_MEDIA_LOCATION", "MEDIA_LOCATION", defaults.MEDIA_LOCATION
    )

    _set(ns, "FORCE_LOCAL_STORAGE", force_local)

    # Bucket name (django-storages reads AWS_STORAGE_BUCKET_NAME for every write).
    bucket_name = resolve(ns, "AWS_STORAGE_BUCKET_NAME", "BUCKET_NAME", "")
    if bucket_name:
        _setdefault(ns, "AWS_STORAGE_BUCKET_NAME", bucket_name)

    # CDN custom domain + derived URLs (only when serving from S3).
    if custom_domain:
        _setdefault(ns, "AWS_S3_CUSTOM_DOMAIN", custom_domain)
        if not force_local:
            _setdefault(ns, "STATIC_URL", f"https://{custom_domain}/static/")
            _setdefault(ns, "MEDIA_URL", f"https://{custom_domain}/media/")

    # Local URLs whenever assets are not served from the CDN: force-local
    # collectstatic, or no custom domain configured. setdefault keeps any CDN URL
    # set above; without this the trailing-slash checks below abort settings import
    # when force_local is set and DEBUG is off (e.g. production collectstatic
    # --force-local-storage), which surfaces as "Unknown command: collectstatic".
    _setdefault(ns, "STATIC_URL", "/static/")
    _setdefault(ns, "MEDIA_URL", "/media/")

    # Ensure STORAGES exists with every alias the storage classes resolve.
    if force_local:
        default_backend = defaults.FILESYSTEM_BACKEND
        static_backend = defaults.STATICFILES_LOCAL_BACKEND
    else:
        default_backend = defaults.MEDIA_S3_BACKEND
        static_backend = (
            defaults.STATICFILES_LOCAL_BACKEND
            if run_compress
            else defaults.STATIC_S3_BACKEND
        )
    private_backend = (
        defaults.FILESYSTEM_BACKEND
        if force_local
        else defaults.PRIVATE_S3_BACKEND
    )
    storages = dict(_get(ns, "STORAGES", {}) or {})
    storages.setdefault("default", {"BACKEND": default_backend})
    storages.setdefault("staticfiles", {"BACKEND": static_backend})
    storages.setdefault("compressor", {"BACKEND": defaults.COMPRESSOR_BACKEND})
    storages.setdefault("local", {"BACKEND": defaults.FILESYSTEM_BACKEND})
    # Private uploads (e.g. confirmation documents) served via signed URLs.
    storages.setdefault("private", {"BACKEND": private_backend})
    _set(ns, "STORAGES", storages)

    # Local-dev overrides. When applied on the already-configured settings object,
    # assign directly (settings.configure() would raise RuntimeError).
    if _get(ns, "DEBUG", False):
        _set(ns, "COMPRESS_ENABLED", False)
        _set(ns, "COMPRESS_OFFLINE", False)
        _set(ns, "STATIC_URL", "/static/")
        # Serve static locally in development; media keeps its resolved backend
        # (S3 unless FORCE_LOCAL), matching the production debug behaviour.
        storages["staticfiles"]["BACKEND"] = defaults.STATICFILES_LOCAL_BACKEND
        storages["private"]["BACKEND"] = defaults.FILESYSTEM_BACKEND
        _set(
            ns,
            "STATICFILES_FINDERS",
            (
                "django.contrib.staticfiles.finders.FileSystemFinder",
                "django.contrib.staticfiles.finders.AppDirectoriesFinder",
            ),
        )
        if os.name == "nt" and _has(ns, "WORK_DIR"):
            work_dir = _get(ns, "WORK_DIR")
            _set(ns, "MEDIA_ROOT", os.path.join(work_dir, "mediaroot"))
            _set(ns, "STATIC_ROOT", os.path.join(work_dir, "staticroot"))

    # S3 location/url/root values consumed by the storage classes.
    static_url = _get(ns, "AWS_S3_STATIC_URL", None) or _get(
        ns, "STATIC_URL", None
    )
    if not static_url or not static_url.endswith("/"):
        raise ImproperlyConfigured(
            "The STATIC_URL and AWS_S3_STATIC_URL settings must have a "
            "trailing slash."
        )
    static_root = _get(ns, "AWS_S3_STATIC_ROOT", None) or _get(
        ns, "STATIC_ROOT", None
    )
    media_url = _get(ns, "AWS_S3_MEDIA_URL", None) or _get(
        ns, "MEDIA_URL", None
    )
    if not media_url or not media_url.endswith("/"):
        raise ImproperlyConfigured(
            "The MEDIA_URL and AWS_S3_MEDIA_URL settings must have a "
            "trailing slash."
        )
    media_root = _get(ns, "AWS_S3_MEDIA_ROOT", None) or _get(
        ns, "MEDIA_ROOT", None
    )
    compress_root = _get(ns, "AWS_S3_COMPRESS_ROOT", None) or static_root
    _set(ns, "COMPRESS_ROOT", compress_root)

    # Expose the S3 location/url/root values so they are readable as settings too.
    _setdefault(ns, "AWS_S3_STATIC_LOCATION", static_location)
    _setdefault(ns, "AWS_S3_STATIC_URL", static_url)
    _setdefault(ns, "AWS_S3_MEDIA_LOCATION", media_location)
    _setdefault(ns, "AWS_S3_MEDIA_URL", media_url)
    if static_root is not None:
        _setdefault(ns, "AWS_S3_STATIC_ROOT", static_root)
    if media_root is not None:
        _setdefault(ns, "AWS_S3_MEDIA_ROOT", media_root)

    # Thumbnail storage. Do not set DEFAULT_FILE_STORAGE: on Django 4.2+ it is
    # mutually exclusive with STORAGES (ImproperlyConfigured) and it was removed
    # in Django 5.1. easy-thumbnails reads THUMBNAIL_DEFAULT_STORAGE directly.
    _setdefault(ns, "THUMBNAIL_DEFAULT_STORAGE", storages["default"]["BACKEND"])

    # Compressor.
    _setdefault(ns, "COMPRESS_OUTPUT_DIR", defaults.COMPRESS_OUTPUT_DIR)
    _setdefault(ns, "COMPRESS_STORAGE", storages["staticfiles"]["BACKEND"])
    _setdefault(ns, "COMPRESS_ENABLED", bool(defaults.COMPRESS_ENABLED))
    _setdefault(ns, "COMPRESS_OFFLINE", bool(defaults.COMPRESS_OFFLINE))
    _setdefault(
        ns, "COMPRESS_CSS_HASHING_METHOD", defaults.COMPRESS_CSS_HASHING_METHOD
    )
    _setdefault(ns, "COMPRESS_CSS_FILTERS", list(defaults.COMPRESS_CSS_FILTERS))
    _setdefault(ns, "COMPRESS_JS_FILTERS", list(defaults.COMPRESS_JS_FILTERS))
    _setdefault(ns, "STATICFILES_FINDERS", tuple(defaults.STATICFILES_FINDERS))

    # django-compressor writes bundles via STORAGES[COMPRESS_STORAGE_ALIAS], not the
    # COMPRESS_STORAGE string when that alias exists. STORAGES["compressor"] must stay
    # on CompressorFileStorage because StaticRootCachedS3Storage uses it as a local
    # cache; route S3 output through a separate alias instead.
    compress_backend = _get(ns, "COMPRESS_STORAGE")
    if (
        not force_local
        and not _get(ns, "DEBUG", False)
        and compress_backend == defaults.STATIC_S3_BACKEND
    ):
        storages.setdefault(
            defaults.COMPRESSOR_OUTPUT_ALIAS,
            {"BACKEND": compress_backend},
        )
        _setdefault(ns, "COMPRESS_STORAGE_ALIAS", defaults.COMPRESSOR_OUTPUT_ALIAS)
        _set(ns, "STORAGES", storages)

    # AWS S3 behaviour.
    _setdefault(
        ns,
        "AWS_S3_FILE_OVERWRITE",
        resolve_bool(
            ns,
            "AWS_S3_FILE_OVERWRITE",
            "FILE_OVERWRITE",
            defaults.AWS_S3_FILE_OVERWRITE,
        ),
    )
    _setdefault(
        ns,
        "AWS_DEFAULT_ACL",
        resolve(ns, "AWS_DEFAULT_ACL", "DEFAULT_ACL", defaults.AWS_DEFAULT_ACL),
    )
    _setdefault(
        ns,
        "AWS_QUERYSTRING_AUTH",
        resolve_bool(
            ns,
            "AWS_QUERYSTRING_AUTH",
            "QUERYSTRING_AUTH",
            defaults.AWS_QUERYSTRING_AUTH,
        ),
    )
    file_expire = int(
        resolve(ns, "AWS_FILE_EXPIRE", "FILE_EXPIRE", defaults.AWS_FILE_EXPIRE)
    )
    _setdefault(ns, "AWS_FILE_EXPIRE", file_expire)
    _setdefault(
        ns,
        "AWS_PRELOAD_METADATA",
        resolve_bool(
            ns,
            "AWS_PRELOAD_METADATA",
            "PRELOAD_METADATA",
            defaults.AWS_PRELOAD_METADATA,
        ),
    )
    _setdefault(
        ns,
        "AWS_S3_OBJECT_PARAMETERS",
        _object_parameters(ns, int(_get(ns, "AWS_FILE_EXPIRE"))),
    )

    # Private uploads (signed, expiring URLs).
    _setdefault(
        ns,
        "AWS_S3_PRIVATE_LOCATION",
        resolve(
            ns,
            "AWS_S3_PRIVATE_LOCATION",
            "PRIVATE_LOCATION",
            defaults.PRIVATE_LOCATION,
        ),
    )
    _setdefault(
        ns,
        "AWS_S3_PRIVATE_URL_EXPIRE",
        int(
            resolve(
                ns,
                "AWS_S3_PRIVATE_URL_EXPIRE",
                "PRIVATE_URL_EXPIRE",
                defaults.PRIVATE_URL_EXPIRE,
            )
        ),
    )

    # HTML minify defaults (used by html-minify middlewares when installed).
    _setdefault(
        ns,
        "KEEP_COMMENTS_ON_MINIFYING",
        bool(defaults.KEEP_COMMENTS_ON_MINIFYING),
    )
    _setdefault(ns, "HTML_MINIFY", bool(defaults.HTML_MINIFY))

    return {
        "AWS_S3_STATIC_LOCATION": static_location,
        "AWS_S3_STATIC_URL": static_url,
        "AWS_S3_STATIC_ROOT": static_root,
        "AWS_S3_MEDIA_LOCATION": media_location,
        "AWS_S3_MEDIA_URL": media_url,
        "AWS_S3_MEDIA_ROOT": media_root,
        "AWS_S3_COMPRESS_ROOT": compress_root,
    }
