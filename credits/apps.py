from django.apps import AppConfig


class CreditsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "credits"

    def ready(self):
        """Importa signals quando o app está pronto."""
        import credits.signals  # noqa: F401

