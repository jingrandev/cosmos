from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomerOrderState(models.TextChoices):
    GREETING = "greeting", _("greeting")
    DAY_REPLY = "day_reply", _("day reply")
    ASK_FAVORITES = "ask_favorites", _("ask favorites")
    FAVORITES_REPLY = "favorites_reply", _("favorites reply")
    ASK_ORDER = "ask_order", _("ask order")
    ORDER_REPLY = "order_reply", _("order reply")
    ANALYZE = "analyze", _("analyze")
    COMPLETE = "complete", _("complete")
