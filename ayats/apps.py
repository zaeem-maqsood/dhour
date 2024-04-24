from django.apps import AppConfig


class AyatsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ayats"

    def ready(self):
        import ayats.signals
