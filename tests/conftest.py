"""Default the S3 write gate to allow during the package test suite.

Production/developer behaviour is covered in ``test_s3_write_gate.py``; other
tests assert S3 backend wiring and must opt in explicitly on Windows.
"""

import os

# Set before Django settings / apply_storage_defaults run.
os.environ.setdefault("CUSTOM_STORAGE_ALLOW_S3_WRITES", "true")
