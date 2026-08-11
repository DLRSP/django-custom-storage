"""S3 object-write gate: env-driven, no hostnames."""

import os
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from custom_storage.conf import get_force_local, get_run_compress, s3_object_writes_denied
from custom_storage.storage import (
    MediaRootCachedS3Storage,
    StaticRootCachedS3Storage,
    _refuse_s3_object_write,
)


class S3ObjectWriteGateTests(SimpleTestCase):
    def test_allow_env_false_denies(self):
        with mock.patch.dict(
            os.environ, {"CUSTOM_STORAGE_ALLOW_S3_WRITES": "False"}, clear=False
        ):
            os.environ.pop("FORCE_LOCAL_STORAGE", None)
            self.assertTrue(s3_object_writes_denied())
            self.assertTrue(get_force_local({"FORCE_LOCAL_STORAGE": False}))
            self.assertFalse(get_run_compress({"RUN_COMPRESS": True}))

    def test_allow_env_true_allows(self):
        with mock.patch.dict(
            os.environ, {"CUSTOM_STORAGE_ALLOW_S3_WRITES": "True"}, clear=False
        ):
            os.environ.pop("FORCE_LOCAL_STORAGE", None)
            with mock.patch("custom_storage.conf.os.name", "posix"):
                self.assertFalse(s3_object_writes_denied())
                self.assertFalse(get_force_local({"FORCE_LOCAL_STORAGE": False}))

    def test_force_local_env_denies(self):
        with mock.patch.dict(os.environ, {"FORCE_LOCAL_STORAGE": "1"}, clear=False):
            os.environ.pop("CUSTOM_STORAGE_ALLOW_S3_WRITES", None)
            with mock.patch("custom_storage.conf.os.name", "posix"):
                self.assertTrue(s3_object_writes_denied())

    def test_windows_denies_by_default(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CUSTOM_STORAGE_ALLOW_S3_WRITES", None)
            os.environ.pop("FORCE_LOCAL_STORAGE", None)
            with mock.patch("custom_storage.conf.os.name", "nt"):
                self.assertTrue(s3_object_writes_denied())

    def test_posix_unset_allows(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CUSTOM_STORAGE_ALLOW_S3_WRITES", None)
            os.environ.pop("FORCE_LOCAL_STORAGE", None)
            with mock.patch("custom_storage.conf.os.name", "posix"):
                self.assertFalse(s3_object_writes_denied())

    def test_refuse_raises(self):
        with mock.patch.dict(
            os.environ, {"CUSTOM_STORAGE_ALLOW_S3_WRITES": "0"}, clear=False
        ):
            with self.assertRaises(ImproperlyConfigured):
                _refuse_s3_object_write("save")

    def test_static_and_media_delete_refused(self):
        with mock.patch.dict(
            os.environ, {"CUSTOM_STORAGE_ALLOW_S3_WRITES": "false"}, clear=False
        ):
            for cls in (StaticRootCachedS3Storage, MediaRootCachedS3Storage):
                with self.assertRaises(ImproperlyConfigured):
                    cls.delete(cls.__new__(cls), "x.css")
