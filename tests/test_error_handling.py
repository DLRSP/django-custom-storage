"""Tests for error handling and fault scenarios"""

from unittest.mock import Mock, patch
from io import BytesIO

from django.test import TestCase
from django.core.files.base import ContentFile

from custom_storage.storage import (
    StaticRootCachedS3Storage,
    MediaRootCachedS3Storage,
    PublicMediaS3Boto3Storage,
    PrivateMediaS3Boto3Storage,
)


class AWSClientErrorTestCase(TestCase):
    """Test handling of AWS boto3 ClientError exceptions"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file_name = "test.txt"
        self.test_content = b"test content"

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_s3_client_error(self, mock_get_storage_class, mock_s3_save):
        """Test that save handles boto3 ClientError exceptions"""
        from botocore.exceptions import ClientError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(self.test_content)

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # Mock S3Storage.save to raise ClientError
        error_response = {
            "Error": {
                "Code": "NoSuchBucket",
                "Message": "The specified bucket does not exist",
            }
        }
        mock_s3_save.side_effect = ClientError(error_response, "PutObject")

        # Save should raise the exception (current behavior)
        with self.assertRaises(ClientError):
            storage.save(self.test_file_name, content)

        # Local storage should still be called
        mock_local_storage._save.assert_called_once()

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_s3_access_denied(self, mock_get_storage_class, mock_s3_save):
        """Test that save handles AccessDenied errors"""
        from botocore.exceptions import ClientError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(self.test_content)

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        error_response = {
            "Error": {
                "Code": "AccessDenied",
                "Message": "Access Denied",
            }
        }
        mock_s3_save.side_effect = ClientError(error_response, "PutObject")

        with self.assertRaises(ClientError):
            storage.save(self.test_file_name, content)

    @patch("custom_storage.storage.S3Storage.delete")
    @patch("custom_storage.storage.get_storage_class")
    def test_delete_handles_s3_client_error(
        self, mock_get_storage_class, mock_s3_delete
    ):
        """Test that delete handles boto3 ClientError exceptions"""
        from botocore.exceptions import ClientError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)

        storage = MediaRootCachedS3Storage()

        # Mock S3Storage.delete to raise ClientError
        error_response = {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "The specified key does not exist",
            }
        }
        mock_s3_delete.side_effect = ClientError(error_response, "DeleteObject")

        # Delete should raise the exception (current behavior)
        with self.assertRaises(ClientError):
            storage.delete(self.test_file_name)

        # Local storage delete should still be called
        mock_local_storage.delete.assert_called()


class AWSConnectionErrorTestCase(TestCase):
    """Test handling of AWS connection errors"""

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_connection_error(self, mock_get_storage_class, mock_s3_save):
        """Test that save handles connection errors"""
        from botocore.exceptions import EndpointConnectionError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(b"content")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")

        mock_s3_save.side_effect = EndpointConnectionError(
            endpoint_url="https://s3.amazonaws.com"
        )

        with self.assertRaises(EndpointConnectionError):
            storage.save("test.txt", content)

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_credential_error(self, mock_get_storage_class, mock_s3_save):
        """Test that save handles credential errors"""
        from botocore.exceptions import NoCredentialsError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(b"content")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")

        mock_s3_save.side_effect = NoCredentialsError()

        with self.assertRaises(NoCredentialsError):
            storage.save("test.txt", content)


class LocalStorageErrorTestCase(TestCase):
    """Test handling of local storage errors"""

    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_local_storage_permission_error(self, mock_get_storage_class):
        """Test that save handles local storage PermissionError"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._save.side_effect = PermissionError("Permission denied")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")

        # Save should raise PermissionError when local storage fails
        with self.assertRaises(PermissionError):
            storage.save("test.txt", content)

    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_local_storage_io_error(self, mock_get_storage_class):
        """Test that save handles local storage IOError"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._save.side_effect = IOError("Disk full")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")

        with self.assertRaises(IOError):
            storage.save("test.txt", content)

    @patch("custom_storage.storage.get_storage_class")
    def test_delete_handles_local_storage_file_not_found(self, mock_get_storage_class):
        """Test that delete handles FileNotFoundError from local storage"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        # Local storage raises FileNotFoundError, but delete continues
        mock_local_storage.delete.side_effect = FileNotFoundError("File not found")

        storage = MediaRootCachedS3Storage()

        # Note: Current implementation doesn't handle FileNotFoundError in delete
        # This test documents current behavior
        with patch("custom_storage.storage.S3Storage.delete"):
            # The exception will propagate
            with self.assertRaises(FileNotFoundError):
                storage.delete("test.jpg")


class MediaStorageDeleteErrorTestCase(TestCase):
    """Test error handling in MediaRootCachedS3Storage.delete"""

    @patch("custom_storage.storage.get_storage_class")
    def test_delete_handles_missing_optimized_files(self, mock_get_storage_class):
        """Test that delete handles missing webp/avif files gracefully"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)

        # Main file exists, optimized files don't
        def delete_side_effect(name):
            if name.endswith((".webp", ".avif")):
                raise FileNotFoundError(f"File {name} not found")
            return None

        mock_local_storage.delete.side_effect = delete_side_effect
        storage = MediaRootCachedS3Storage()

        # Note: Current implementation doesn't catch FileNotFoundError
        # This test documents the behavior - exceptions are raised
        with patch("custom_storage.storage.S3Storage.delete"):
            # Will raise FileNotFoundError when trying to delete webp/avif
            with self.assertRaises(FileNotFoundError):
                storage.delete("test.jpg")

    @patch("custom_storage.storage.S3Storage.delete")
    @patch("custom_storage.storage.get_storage_class")
    def test_delete_handles_s3_error_for_optimized_files(
        self, mock_get_storage_class, mock_s3_delete
    ):
        """Test that delete handles S3 errors for optimized files"""
        from botocore.exceptions import ClientError

        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)

        storage = MediaRootCachedS3Storage()

        error_response = {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "The specified key does not exist",
            }
        }

        # First call succeeds (main file), subsequent calls fail (optimized files)
        call_count = [0]

        def delete_side_effect(name):
            call_count[0] += 1
            if call_count[0] > 1:  # After main file
                raise ClientError(error_response, "DeleteObject")
            return None

        mock_s3_delete.side_effect = delete_side_effect

        # Delete should raise ClientError when trying to delete optimized files
        with self.assertRaises(ClientError):
            storage.delete("test.jpg")


class StorageInitializationErrorTestCase(TestCase):
    """Test error handling during storage initialization"""

    @patch("custom_storage.storage.get_storage_class")
    def test_init_handles_invalid_storage_backend(self, mock_get_storage_class):
        """Test that initialization handles invalid storage backend"""
        # Mock get_storage_class to raise ImportError
        mock_get_storage_class.side_effect = ImportError(
            "No module named 'invalid.storage'"
        )

        # Should raise ImportError during initialization
        with self.assertRaises(ImportError):
            StaticRootCachedS3Storage()

    @patch("custom_storage.storage.get_storage_class")
    def test_init_handles_missing_storages_config(self, mock_get_storage_class):
        """Test that initialization handles missing STORAGES config"""
        with patch("django.conf.settings.STORAGES", new={}):
            # If STORAGES is empty, accessing "compressor" will raise KeyError
            with self.assertRaises(KeyError):
                StaticRootCachedS3Storage()


class S3StorageBackendErrorTestCase(TestCase):
    """Test S3Storage backend specific errors"""

    def test_public_media_storage_attributes(self):
        """Test that PublicMediaS3Boto3Storage has correct error-prone attributes"""
        storage = PublicMediaS3Boto3Storage()
        # These attributes should be set correctly to avoid configuration errors
        self.assertEqual(storage.location, "media")
        self.assertEqual(storage.default_acl, "public-read")
        self.assertFalse(storage.file_overwrite)

    def test_private_media_storage_attributes(self):
        """Test that PrivateMediaS3Boto3Storage has correct error-prone attributes"""
        storage = PrivateMediaS3Boto3Storage()
        # These attributes should be set correctly to avoid configuration errors
        self.assertEqual(storage.location, "private")
        self.assertEqual(storage.default_acl, "private")
        self.assertFalse(storage.file_overwrite)
        self.assertFalse(storage.custom_domain)


class RetryAndResilienceTestCase(TestCase):
    """Test retry and resilience scenarios (documenting current behavior)"""

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_local_first_then_s3(self, mock_get_storage_class, mock_s3_save):
        """Test that save saves to local first, then S3 (local failure prevents S3 save)"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._save.side_effect = IOError("Local storage failed")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")

        # If local storage fails, S3 save should not be attempted
        with self.assertRaises(IOError):
            storage.save("test.txt", content)

        # S3 save should not be called if local save fails
        mock_s3_save.assert_not_called()

    @patch("custom_storage.storage.S3Storage.delete")
    @patch("custom_storage.storage.get_storage_class")
    def test_delete_local_and_s3_both_called(
        self, mock_get_storage_class, mock_s3_delete
    ):
        """Test that delete attempts both local and S3 deletion"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)

        storage = MediaRootCachedS3Storage()

        storage.delete("test.jpg")

        # Both local and S3 delete should be called
        self.assertGreater(mock_local_storage.delete.call_count, 0)
        self.assertGreater(mock_s3_delete.call_count, 0)


class EdgeCaseErrorTestCase(TestCase):
    """Test edge case error scenarios"""

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_with_empty_content(self, mock_get_storage_class, mock_s3_save):
        """Test save with empty content (should not cause errors)"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(b"")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"")

        result = storage.save("empty.txt", content)
        self.assertEqual(result, "empty.txt")
        mock_s3_save.assert_called_once()

    @patch("custom_storage.storage.S3Storage.delete")
    @patch("custom_storage.storage.get_storage_class")
    def test_delete_with_special_characters_in_name(
        self, mock_get_storage_class, mock_s3_delete
    ):
        """Test delete with special characters in filename"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)

        storage = MediaRootCachedS3Storage()

        # Test with special characters
        storage.delete("file with spaces.jpg")
        storage.delete("file@special#chars.jpg")
        storage.delete("file/with/path.jpg")

        # Should handle these gracefully
        self.assertGreater(mock_local_storage.delete.call_count, 0)
        self.assertGreater(mock_s3_delete.call_count, 0)

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_with_very_long_filename(self, mock_get_storage_class, mock_s3_save):
        """Test save with very long filename"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(b"content")

        storage = StaticRootCachedS3Storage()
        content = ContentFile(b"test content")
        long_filename = "a" * 300 + ".txt"  # Very long filename

        # Should handle long filenames (may be truncated by S3)
        result = storage.save(long_filename, content)
        self.assertEqual(result, long_filename)


class CompressorFileStorageErrorTestCase(TestCase):
    """Test error handling for django-compressor CompressorFileStorage integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_file_name = "test.css"
        self.test_content = b"body { color: red; }"

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_compressor_open_error(
        self, mock_get_storage_class, mock_s3_save
    ):
        """Test that save handles errors when CompressorFileStorage._open() fails after _save()"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        # _save succeeds, but _open fails
        mock_local_storage._save.return_value = None
        mock_local_storage._open.side_effect = IOError(
            "Failed to open file from compressor storage"
        )

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # If _open fails after _save, S3 save should not be attempted
        with self.assertRaises(IOError):
            storage.save(self.test_file_name, content)

        # Verify _save was called
        mock_local_storage._save.assert_called_once()
        # Verify _open was called (and failed)
        mock_local_storage._open.assert_called_once()
        # S3 save should not be called if _open fails
        mock_s3_save.assert_not_called()

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_compressor_file_not_found(
        self, mock_get_storage_class, mock_s3_save
    ):
        """Test that save handles FileNotFoundError when CompressorFileStorage._open() can't find the file"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        # _save succeeds, but _open can't find the file
        mock_local_storage._save.return_value = None
        mock_local_storage._open.side_effect = FileNotFoundError(
            "File not found in compressor storage"
        )

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # If _open raises FileNotFoundError, S3 save should not be attempted
        with self.assertRaises(FileNotFoundError):
            storage.save(self.test_file_name, content)

        # Verify _save was called
        mock_local_storage._save.assert_called_once()
        # S3 save should not be called if _open fails
        mock_s3_save.assert_not_called()

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_compressor_permission_error(
        self, mock_get_storage_class, mock_s3_save
    ):
        """Test that save handles PermissionError when CompressorFileStorage._open() fails due to permissions"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        # _save succeeds, but _open fails due to permissions
        mock_local_storage._save.return_value = None
        mock_local_storage._open.side_effect = PermissionError(
            "Permission denied accessing compressor storage"
        )

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # If _open raises PermissionError, S3 save should not be attempted
        with self.assertRaises(PermissionError):
            storage.save(self.test_file_name, content)

        # Verify _save was called
        mock_local_storage._save.assert_called_once()
        # S3 save should not be called if _open fails
        mock_s3_save.assert_not_called()

    @patch("custom_storage.storage.get_storage_class")
    def test_init_handles_invalid_compressor_backend(self, mock_get_storage_class):
        """Test that initialization handles invalid compressor storage backend"""
        # Mock get_storage_class to raise ImportError for invalid compressor backend
        mock_get_storage_class.side_effect = ImportError(
            "No module named 'compressor.storage.CompressorFileStorage'"
        )

        # Should raise ImportError during initialization
        with self.assertRaises(ImportError):
            StaticRootCachedS3Storage()

    @patch("custom_storage.storage.get_storage_class")
    def test_init_handles_compressor_storage_initialization_error(
        self, mock_get_storage_class
    ):
        """Test that initialization handles errors when CompressorFileStorage can't be instantiated"""
        from django.core.exceptions import ImproperlyConfigured

        # Mock get_storage_class to return a class that raises an error when instantiated
        class FailingCompressorStorage:
            def __init__(self):
                raise ImproperlyConfigured("COMPRESS_ROOT is not configured correctly")

        mock_get_storage_class.return_value = FailingCompressorStorage

        # Should raise ImproperlyConfigured during initialization
        with self.assertRaises(ImproperlyConfigured):
            StaticRootCachedS3Storage()

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_uses_compressor_storage_correctly(
        self, mock_get_storage_class, mock_s3_save
    ):
        """Test that save uses CompressorFileStorage correctly (verifies integration)"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        mock_local_storage._open.return_value = BytesIO(self.test_content)

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # Save should succeed
        result = storage.save(self.test_file_name, content)

        # Verify CompressorFileStorage methods were called
        mock_local_storage._save.assert_called_once_with(self.test_file_name, content)
        mock_local_storage._open.assert_called_once_with(self.test_file_name)
        # Verify S3 save was called with the opened file
        mock_s3_save.assert_called_once()
        # Verify the correct storage class was requested
        from django.conf import settings

        mock_get_storage_class.assert_called_with(
            settings.STORAGES["compressor"]["BACKEND"]
        )
        self.assertEqual(result, self.test_file_name)

    @patch("custom_storage.storage.get_storage_class")
    def test_static_storage_uses_compressor_backend(self, mock_get_storage_class):
        """Test that StaticRootCachedS3Storage uses compressor backend from STORAGES"""
        mock_compressor_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_compressor_storage)

        storage = StaticRootCachedS3Storage()

        # Verify that get_storage_class was called with compressor backend
        from django.conf import settings

        mock_get_storage_class.assert_called_with(
            settings.STORAGES["compressor"]["BACKEND"]
        )
        # Verify that local_storage is set to the compressor storage instance
        self.assertEqual(storage.local_storage, mock_compressor_storage)

    @patch("custom_storage.storage.S3Storage.save")
    @patch("custom_storage.storage.get_storage_class")
    def test_save_handles_compressor_storage_os_error(
        self, mock_get_storage_class, mock_s3_save
    ):
        """Test that save handles OSError when CompressorFileStorage operations fail"""
        mock_local_storage = Mock()
        mock_get_storage_class.return_value = Mock(return_value=mock_local_storage)
        # _save succeeds, but _open raises OSError
        mock_local_storage._save.return_value = None
        mock_local_storage._open.side_effect = OSError(
            "OS error accessing compressor storage"
        )

        storage = StaticRootCachedS3Storage()
        content = ContentFile(self.test_content)

        # If _open raises OSError, S3 save should not be attempted
        with self.assertRaises(OSError):
            storage.save(self.test_file_name, content)

        # Verify _save was called
        mock_local_storage._save.assert_called_once()
        # S3 save should not be called if _open fails
        mock_s3_save.assert_not_called()
