import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthConfig(AppConfig):
    name = "core.auth"
    label = "authentication"
    verbose_name = _("Authentication")

    def ready(self):
        with contextlib.suppress(ImportError):
            import core.auth.signals  # noqa: F401
