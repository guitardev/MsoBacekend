# main/apps.py

from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Configuration for the 'main' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """
        This method is called when Django starts up.
        It's a good place to import signals or other code that needs to be executed once the app is ready.
        """
        import main.signals  # Import your signals module
