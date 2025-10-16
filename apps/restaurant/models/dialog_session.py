from django.db import models
from django.utils.translation import gettext_lazy as _

from core.db.models import BaseModel


class DialogSession(BaseModel):
    class CustomerOrderState(models.TextChoices):
        INIT = "init", _("init")
        GREETING = "greeting", _("greeting")
        DAY_REPLY = "day_reply", _("day reply")
        ASK_FAVORITES = "ask_favorites", _("ask favorites")
        FAVORITES_REPLY = "favorites_reply", _("favorites reply")
        ASK_ORDER = "ask_order", _("ask order")
        ORDER_REPLY = "order_reply", _("order reply")
        ANALYZE = "analyze", _("analyze")
        COMPLETE = "complete", _("complete")

    state = models.CharField(
        _("state"),
        max_length=32,
        choices=CustomerOrderState.choices,
        default=CustomerOrderState.INIT,
        db_index=True,
    )
    messages = models.JSONField(_("messages"), default=list)
    analysis_result = models.JSONField(_("analysis result"), default=dict)
    customer_favorite_text = models.TextField(_("customer favorite text"), default="")
    customer_order_text = models.TextField(_("customer order text"), default="")
    customer = models.ForeignKey(
        "restaurant.CustomerProfile",
        related_name="dialogs",
        db_index=True,
        db_constraint=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "restaurant_conversation_session"
