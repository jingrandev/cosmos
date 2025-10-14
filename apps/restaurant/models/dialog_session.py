from django.db import models
from django.utils.translation import gettext_lazy as _

from core.db.models import BaseModel


class DialogSession(BaseModel):
    class CustomerOrderState(models.TextChoices):
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
        default=CustomerOrderState.GREETING,
        db_index=True,
    )
    messages = models.JSONField(_("messages"), default=list)
    analysis_result = models.JSONField(_("analysis result"), default=dict)

    class Meta:
        db_table = "restaurant_conversation_session"
