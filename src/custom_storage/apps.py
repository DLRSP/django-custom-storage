from django.apps import AppConfig


class CustomStorageConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "custom_storage"
    verbose_name = "Custom Storage"

    def ready(self):
        # Backward compatibility: projects that do not call
        # apply_storage_defaults() from their settings.py still get the defaults.
        # This is a no-op when every value is already defined.
        from django.conf import settings

        from .conf import apply_storage_defaults

        apply_storage_defaults(settings)
