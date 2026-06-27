"""Tests for APP_CONFIG-based resolution and default injection.

These exercise :func:`custom_storage.conf.apply_storage_defaults` on a plain
namespace dict (as a project ``settings.py`` would pass ``globals()``), so they are
independent of the live Django settings object.
"""

import pytest
from django.core.exceptions import ImproperlyConfigured

from custom_storage import defaults
from custom_storage.conf import apply_storage_defaults


def base_ns(**override):
    ns = {
        "DEBUG": False,
        "STATIC_ROOT": "/srv/static/",
        "MEDIA_ROOT": "/srv/media/",
        "APP_CONFIG": {
            "custom_storage": {
                "BUCKET_NAME": "proj",
                "CUSTOM_DOMAIN": "cdn.proj.eu",
            }
        },
    }
    ns.update(override)
    return ns


def test_s1_package_applies_common_defaults():
    ns = base_ns()
    apply_storage_defaults(ns)
    assert ns["COMPRESS_ENABLED"] is True
    assert ns["COMPRESS_OFFLINE"] is True
    assert ns["AWS_DEFAULT_ACL"] == defaults.AWS_DEFAULT_ACL
    assert ns["AWS_FILE_EXPIRE"] == defaults.AWS_FILE_EXPIRE
    assert ns["COMPRESS_OUTPUT_DIR"] == defaults.COMPRESS_OUTPUT_DIR
    assert "compressor.finders.CompressorFinder" in ns["STATICFILES_FINDERS"]
    assert ns["THUMBNAIL_DEFAULT_STORAGE"] == ns["DEFAULT_FILE_STORAGE"]
    for alias in ("default", "staticfiles", "compressor", "local"):
        assert alias in ns["STORAGES"]


def test_s2_app_config_override():
    ns = base_ns()
    ns["APP_CONFIG"]["custom_storage"]["FILE_EXPIRE"] = 200
    apply_storage_defaults(ns)
    assert ns["AWS_FILE_EXPIRE"] == 200


def test_s3_top_level_wins_over_default():
    ns = base_ns(AWS_DEFAULT_ACL="private")
    apply_storage_defaults(ns)
    assert ns["AWS_DEFAULT_ACL"] == "private"


def test_s3b_top_level_wins_over_app_config():
    ns = base_ns(AWS_FILE_EXPIRE=999)
    ns["APP_CONFIG"]["custom_storage"]["FILE_EXPIRE"] = 200
    apply_storage_defaults(ns)
    assert ns["AWS_FILE_EXPIRE"] == 999


def test_s4_object_parameters_merge():
    ns = base_ns()
    ns["APP_CONFIG"]["custom_storage"]["OBJECT_PARAMETERS"] = {
        "ContentDisposition": "inline"
    }
    apply_storage_defaults(ns)
    params = ns["AWS_S3_OBJECT_PARAMETERS"]
    assert params["ContentDisposition"] == "inline"
    assert "Expires" in params
    assert params["CacheControl"].startswith("max-age=")


def test_s5_storages_built_for_s3():
    ns = base_ns()
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["default"]["BACKEND"] == defaults.MEDIA_S3_BACKEND
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"] == defaults.STATIC_S3_BACKEND
    )
    assert (
        ns["STORAGES"]["compressor"]["BACKEND"] == defaults.COMPRESSOR_BACKEND
    )
    assert ns["STORAGES"]["local"]["BACKEND"] == defaults.FILESYSTEM_BACKEND


def test_s5b_existing_storage_alias_not_clobbered():
    ns = base_ns(
        STORAGES={"default": {"BACKEND": "myapp.storage.Custom"}},
    )
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["default"]["BACKEND"] == "myapp.storage.Custom"
    assert "compressor" in ns["STORAGES"]


def test_s6_debug_flips_to_local():
    ns = base_ns(DEBUG=True)
    apply_storage_defaults(ns)
    assert ns["COMPRESS_ENABLED"] is False
    assert ns["COMPRESS_OFFLINE"] is False
    assert ns["STATIC_URL"] == "/static/"
    # DEBUG serves static locally; media (default) keeps its S3 backend.
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"]
        == defaults.STATICFILES_LOCAL_BACKEND
    )
    assert ns["STORAGES"]["default"]["BACKEND"] == defaults.MEDIA_S3_BACKEND


def test_s7_force_local_storage():
    ns = base_ns(
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
    )
    ns["APP_CONFIG"]["custom_storage"]["FORCE_LOCAL"] = True
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["default"]["BACKEND"] == defaults.FILESYSTEM_BACKEND
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"]
        == defaults.STATICFILES_LOCAL_BACKEND
    )


def test_s8_run_compress_env(monkeypatch):
    monkeypatch.setenv("RUN_COMPRESS", "1")
    ns = base_ns()
    apply_storage_defaults(ns)
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"]
        == defaults.STATICFILES_LOCAL_BACKEND
    )


def test_s8b_run_compress_unset(monkeypatch):
    monkeypatch.delenv("RUN_COMPRESS", raising=False)
    ns = base_ns()
    apply_storage_defaults(ns)
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"] == defaults.STATIC_S3_BACKEND
    )


def test_s8c_run_compress_falsey_string(monkeypatch):
    monkeypatch.setenv("RUN_COMPRESS", "0")
    ns = base_ns()
    apply_storage_defaults(ns)
    assert (
        ns["STORAGES"]["staticfiles"]["BACKEND"] == defaults.STATIC_S3_BACKEND
    )


def test_bucket_name_propagated_from_app_config():
    ns = base_ns()
    # Only APP_CONFIG declares the bucket; no top-level AWS_STORAGE_BUCKET_NAME.
    assert "AWS_STORAGE_BUCKET_NAME" not in ns
    apply_storage_defaults(ns)
    assert ns["AWS_STORAGE_BUCKET_NAME"] == "proj"


def test_private_location_and_expire_configurable():
    ns = base_ns()
    ns["APP_CONFIG"]["custom_storage"]["PRIVATE_LOCATION"] = "piva-docs"
    ns["APP_CONFIG"]["custom_storage"]["PRIVATE_URL_EXPIRE"] = 120
    apply_storage_defaults(ns)
    assert ns["AWS_S3_PRIVATE_LOCATION"] == "piva-docs"
    assert ns["AWS_S3_PRIVATE_URL_EXPIRE"] == 120


def test_s9_trailing_slash_validation():
    ns = base_ns(STATIC_URL="/static")  # missing trailing slash
    del ns["APP_CONFIG"]["custom_storage"]["CUSTOM_DOMAIN"]
    with pytest.raises(ImproperlyConfigured):
        apply_storage_defaults(ns)


def test_s10_static_url_derived_from_custom_domain():
    ns = base_ns()
    apply_storage_defaults(ns)
    assert ns["STATIC_URL"] == "https://cdn.proj.eu/static/"
    assert ns["MEDIA_URL"] == "https://cdn.proj.eu/media/"


def test_s10b_existing_static_url_not_overwritten():
    ns = base_ns(STATIC_URL="/static/", MEDIA_URL="/media/")
    apply_storage_defaults(ns)
    assert ns["STATIC_URL"] == "/static/"
    assert ns["MEDIA_URL"] == "/media/"


def test_s11_idempotent_apply():
    ns = base_ns()
    first = apply_storage_defaults(ns)
    snapshot = dict(ns)
    second = apply_storage_defaults(ns)
    assert first == second
    assert ns["STORAGES"] == snapshot["STORAGES"]
    assert ns["AWS_FILE_EXPIRE"] == snapshot["AWS_FILE_EXPIRE"]


def test_private_alias_uses_s3_backend():
    ns = base_ns()
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["private"]["BACKEND"] == defaults.PRIVATE_S3_BACKEND


def test_private_alias_local_when_force_local():
    ns = base_ns(STATIC_URL="/static/", MEDIA_URL="/media/")
    ns["APP_CONFIG"]["custom_storage"]["FORCE_LOCAL"] = True
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["private"]["BACKEND"] == defaults.FILESYSTEM_BACKEND


def test_private_alias_local_in_debug():
    ns = base_ns(DEBUG=True)
    apply_storage_defaults(ns)
    assert ns["STORAGES"]["private"]["BACKEND"] == defaults.FILESYSTEM_BACKEND


def test_private_storage_class_signs_urls():
    from custom_storage.storage import PrivateMediaS3Boto3Storage

    assert PrivateMediaS3Boto3Storage.default_acl == "private"
    assert PrivateMediaS3Boto3Storage.querystring_auth is True
    assert PrivateMediaS3Boto3Storage.custom_domain is False
    assert PrivateMediaS3Boto3Storage.location == defaults.PRIVATE_LOCATION


def test_returns_resolved_locations():
    ns = base_ns()
    resolved = apply_storage_defaults(ns)
    assert resolved["AWS_S3_STATIC_LOCATION"] == defaults.STATIC_LOCATION
    assert resolved["AWS_S3_MEDIA_LOCATION"] == defaults.MEDIA_LOCATION
    assert resolved["AWS_S3_STATIC_URL"].endswith("/")
    assert resolved["AWS_S3_MEDIA_URL"].endswith("/")
