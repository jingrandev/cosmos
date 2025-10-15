from django.apps import AppConfig


class RestaurantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.restaurant"

    def ready(self):
        # Import signal handlers to ensure they are registered
        # when the app is ready
        import apps.restaurant.signals.handle_user_created  # noqa: F401
