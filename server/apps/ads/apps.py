from django.apps import AppConfig


class AdsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "server.apps.ads"

    def ready(self):
        from . import signals  # noqa
