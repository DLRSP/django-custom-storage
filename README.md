# django-custom-storage [![PyPi license](https://img.shields.io/pypi/l/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)

[![PyPi status](https://img.shields.io/pypi/status/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi version](https://img.shields.io/pypi/v/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi python version](https://img.shields.io/pypi/pyversions/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dm/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dw/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)
[![PyPi downloads](https://img.shields.io/pypi/dd/django-custom-storage.svg)](https://pypi.python.org/pypi/django-custom-storage)

## GitHub ![GitHub release](https://img.shields.io/github/tag/DLRSP/django-custom-storage.svg) ![GitHub release](https://img.shields.io/github/release/DLRSP/django-custom-storage.svg)

## Test [![codecov.io](https://codecov.io/github/DLRSP/django-custom-storage/coverage.svg?branch=main)](https://codecov.io/github/DLRSP/django-custom-storage?branch=main) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DLRSP/django-custom-storage/main.svg)](https://results.pre-commit.ci/latest/github/DLRSP/django-custom-storage/main) [![gitthub.com](https://github.com/DLRSP/django-custom-storage/actions/workflows/ci.yaml/badge.svg)](https://github.com/DLRSP/django-custom-storage/actions/workflows/ci.yaml)

## Check Demo Project
* Check the demo repo on [GitHub](https://github.com/DLRSP/example/tree/django-custom-storage)

## Requirements
-   Python 3.10+ supported.
-   Django 4.2+ supported.

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

3. Configure storage in `settings.py`. The package ships sensible defaults and reads the
   project specifics from `APP_CONFIG["custom_storage"]`; call `apply_storage_defaults`
   at the end of the file so the `STORAGES`, compression and AWS settings are derived for
   you:
```python
# Project paths (kept in the project; not owned by the package)
MEDIA_ROOT = "/var/opt/your_project_name/mediaroot/"
STATIC_ROOT = "/var/cache/your_project_name/staticroot/"

# AWS credentials
AWS_ACCESS_KEY_ID = "YOUR_PROJECT_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_PROJECT_AWS_SECRET_ACCESS_KEY"

# Project-specific options; everything else falls back to the package defaults.
APP_CONFIG = {
    "custom_storage": {
        "BUCKET_NAME": "your_project_bucket_name",
        "CUSTOM_DOMAIN": "cdn.your_project_bucket_name.com",
        # Optional overrides: FILE_EXPIRE, DEFAULT_ACL, PRIVATE_LOCATION, ...
    },
}

from custom_storage.conf import apply_storage_defaults

apply_storage_defaults(globals())
```

   Top-level Django settings always win, so projects that already declare `STORAGES`,
   `COMPRESS_*` or `AWS_*` keep working unchanged. To serve assets from the local
   filesystem (handy in development) start the server with `--force-local-storage` or set
   `FORCE_LOCAL_STORAGE = True`.

   See [Settings](docs/tutorial/settings.md) for every available key and
   [Storage classes](docs/tutorial/storage-classes.md) for the backends, including the
   `private` storage that serves non-public uploads through signed, expiring URLs.


## Run Example Project

```shell
git clone --depth=50 --branch=django-custom-storage https://github.com/DLRSP/example.git DLRSP/example
cd DLRSP/example
python manage.py runserver
```

Now browser the app @ http://127.0.0.1:8000
