from django.apps import AppConfig


class ScrapappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scrapapp'

    def ready(self):
        import scrapapp.signals