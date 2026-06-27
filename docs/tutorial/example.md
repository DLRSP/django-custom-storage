# Example Project

This guide walks you through setting up a complete Django project with django-custom-storage.

## Project Setup

Let's create a simple Django project that uses django-custom-storage for handling static and media files.

### 1. Create a Django Project

```bash
django-admin startproject myproject
cd myproject
```

### 2. Install Dependencies

Create a `requirements.txt` file:

```text
Django>=3.2
django-custom-storage
django-storages[s3]
django-compressor
boto3
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Update settings.py

Update your `settings.py` file:

```python
import os
import sys
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'custom_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AWS S3 Configuration
AWS_STORAGE_BUCKET_PREFIX = "cdn"
AWS_STORAGE_BUCKET_NAME = "myproject-bucket"
AWS_STORAGE_BUCKET_TLD = "com"
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')

# Custom Storage Configuration
if not os.getenv('FORCE_LOCAL_STORAGE', False):
    # Use S3 storage
    STORAGES = {
        "default": {
            "BACKEND": "custom_storage.storage.MediaRootCachedS3Storage",
        },
        "staticfiles": {
            "BACKEND": "custom_storage.storage.StaticRootCachedS3Storage",
        },
    }

    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_PREFIX}.{AWS_STORAGE_BUCKET_NAME}.{AWS_STORAGE_BUCKET_TLD}"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Use local storage for development
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# django-compressor Configuration
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_STORAGE = 'custom_storage.storage.StaticRootCachedS3Storage'
COMPRESS_ROOT = STATIC_ROOT

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

### 4. Create a Test App

Create a simple app to test file uploads:

```bash
python manage.py startapp myapp
```

Add `myapp` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'myapp',
]
```

Create a simple model in `myapp/models.py`:

```python
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

Create and run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Simple View

Create a view in `myapp/views.py`:

```python
from django.shortcuts import render, redirect
from .models import Document

def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        if title and file:
            Document.objects.create(title=title, file=file)
            return redirect('upload_document')
    documents = Document.objects.all()
    return render(request, 'myapp/upload.html', {'documents': documents})
```

Create a template `myapp/templates/myapp/upload.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>File Upload</title>
</head>
<body>
    <h1>Upload Document</h1>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <p>
            <label for="title">Title:</label>
            <input type="text" name="title" id="title" required>
        </p>
        <p>
            <label for="file">File:</label>
            <input type="file" name="file" id="file" required>
        </p>
        <button type="submit">Upload</button>
    </form>

    <h2>Uploaded Documents</h2>
    <ul>
        {% for doc in documents %}
        <li>
            <a href="{{ doc.file.url }}">{{ doc.title }}</a>
        </li>
        {% endfor %}
    </ul>
</body>
</html>
```

### 6. Configure URLs

Update `myproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_document, name='upload_document'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 7. Run the Development Server

For local development (without S3):

```bash
export FORCE_LOCAL_STORAGE=True
python manage.py runserver
```

For production (with S3):

```bash
python manage.py runserver
```

### 8. Test File Upload

1. Visit `http://127.0.0.1:8000/`
2. Upload a file
3. Check that the file is saved both locally and on S3 (if configured)

## Using Static Files

To use static files with compression:

1. Create static files in your app's `static` directory
2. Run `python manage.py collectstatic` to collect static files
3. Run `python manage.py compress` to compress static files (if using compressor)

## Example with FORCE_LOCAL_STORAGE

You can force local storage for development by setting an environment variable:

```bash
export FORCE_LOCAL_STORAGE=True
python manage.py runserver
```

Or by modifying `settings.py` to always use local storage in DEBUG mode.

## Demo Project

Check out the complete demo project on GitHub:
https://github.com/DLRSP/example/tree/django-custom-storage
