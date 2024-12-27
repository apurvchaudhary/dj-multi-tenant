from django.apps import AppConfig


class MtAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mt_app"

    def ready(self):
        import mt_app.signals  # noqa: F401
