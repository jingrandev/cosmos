from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.restaurant.models import CustomerProfile


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if not CustomerProfile.objects.filter(user=instance).exists():
        CustomerProfile.objects.create(user=instance)
