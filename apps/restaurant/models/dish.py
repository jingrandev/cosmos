from django.db import models
from django.utils.translation import gettext_lazy as _

from core.db.models import BaseModel


class Dish(BaseModel):
    name = models.CharField(_("dish name"), max_length=64, unique=True)
    description = models.TextField(_("dish description"))
    ingredients = models.JSONField(_("ingredients"), default=list)

    class Meta:
        db_table = "restaurant_dish"
