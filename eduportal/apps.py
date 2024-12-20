from django.apps import AppConfig


class EduportalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eduportal"

    def ready(self) -> None:
        import eduportal.signals.handlers 
