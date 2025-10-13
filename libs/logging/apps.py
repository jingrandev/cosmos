from django.apps import AppConfig

from libs.logging.setup import setup_logging


class LoggingConfig(AppConfig):
    name = "libs.logging"

    def ready(self):
        setup_logging()
