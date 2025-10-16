from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.db.models import BaseModel


class CustomerProfile(BaseModel):
    class DietaryPreference(models.TextChoices):
        VEGAN = "vegan", _("vegan")
        VEGETARIAN = "vegetarian", _("vegetarian")
        NON_VEGETARIAN = "non-vegetarian", _("non-vegetarian")
        UNKNOWN = "unknown", _("unknown")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_index=True,
        related_name="customer",
    )
    dietary_preference = models.CharField(
        _("dietary preference"),
        max_length=64,
        choices=DietaryPreference.choices,
        default=DietaryPreference.UNKNOWN,
    )
    favorite_dishes = models.JSONField(
        _("favorite dishes"),
        default=list,
    )

    class Meta:
        db_table = "restaurant_customer"
