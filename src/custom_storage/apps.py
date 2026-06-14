# coding: utf-8
from django.apps import AppConfig


class CustomStorageConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "custom_storage"
    verbose_name = "Custom Storage"

    def ready(self):
        from . import settings  # noqa: F401
