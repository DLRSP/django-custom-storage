# django-custom-storage [![PyPi license](https://img.shields.io/pypi/l/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)

[![PyPi status](https://img.shields.io/pypi/status/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi version](https://img.shields.io/pypi/v/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi python version](https://img.shields.io/pypi/pyversions/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dm/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dw/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dd/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-custom-storage.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-custom-storage.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-custom-storage/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-custom-storage?branch=main) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DLRSP/django-custom-storage/main.svg)](https://results.pre-commit.ci/latest/github/DLRSP/django-custom-storage/main) [![gitthub.com](https://github.com/DLRSP/django-custom-storage/actions/workflows/ci.yml/badge.svg)](https://github.com/DLRSP/django-custom-storage/actions/workflows/ci.yml)

## Check Demo Project
* Check the demo repo on [GitHub](https://github.com/DLRSP/example/tree/django-custom-storage)

## Requirements
-   Python 3.8+ supported.
-   Django 3.2+ supported.

## Setup
1. Install from **pip**:
```shell
pip install django-custom-storage
```

2. Modify `settings.py` by adding the app to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "compressor",
    "custom_storage",
    # ...
]
```

3. Finally, Modify `settings.py` by adding the needed configurations:
```python
# ...other setting...
# Media files (Uploaded Images, Documents, Video, Audio)
MEDIA_ROOT = '/var/opt/your_project_name/mediaroot/'
# Static files (Fonts, CSS, JavaScript, Icons, Theme's Images)
STATIC_URL = '/static/'
STATIC_ROOT = '/var/cache/your_project_name/staticroot/'

# Example: cdn.your_project_bucket_name.com
AWS_STORAGE_BUCKET_PREFIX = "cdn"
AWS_STORAGE_BUCKET_NAME = "your_project_bucket_name"
AWS_STORAGE_BUCKET_TLD = "com"

# Access Key ID & Secret Access Key
AWS_ACCESS_KEY_ID = 'YOUR_PROJECT_AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_PROJECT_AWS_SECRET_ACCESS_KEY'
# ...other setting...

# START - Compress and Upload on S3
import os
import sys
import datetime

# Add option to FORCE_LOCAL_STORAGE
# https://www.mslinn.com/django/1300-django-aws-control.html
if "--force-local-storage" in sys.argv:
    print("AWS datastore disabled; using local storage for assets instead.")
    FORCE_LOCAL_STORAGE = True
    sys.argv.remove("--force-local-storage")
else:
    print("Using AWS datastore for assets.")
    FORCE_LOCAL_STORAGE = False

if not FORCE_LOCAL_STORAGE:
    DEFAULT_FILE_STORAGE = 'custom_storage.storage.MediaRootCachedS3Storage'
    if not os.getenv('RUN_COMPRESS', False):
        STATICFILES_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_ROOT = STATIC_ROOT

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}"

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
AWS_S3_OBJECT_PARAMETERS = {
    'Expires': expires,
    'CacheControl': 'max-age=%d' % (int(two_months.total_seconds()),),
}

COMPRESS_CSS_HASHING_METHOD = None
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    # 'compressor.filters.css_default.CssRelativeFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_OUTPUT_DIR = 'compressed_static'
COMPRESS_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
# END - Compress and Upload on S3

```


## Run Example Project

```shell
git clone --depth=50 --branch=django-custom-storage https://github.com/DLRSP/example.git DLRSP/example
cd DLRSP/example
python manage.py runserver
```

Now browser the app @ http://127.0.0.1:8000
