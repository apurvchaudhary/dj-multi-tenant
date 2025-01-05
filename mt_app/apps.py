from django.apps import AppConfig


class MtAppConfig(AppConfig):
    name = "mt_app"

    def ready(self):
        import mt_app.signals  # noqa: F401
