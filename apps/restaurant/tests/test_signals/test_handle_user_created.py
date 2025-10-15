from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.restaurant.models import CustomerProfile


class TestHandleUserCreatedSignal(TestCase):
    def test_profile_created_on_user_creation(self):
        User = get_user_model()
        user = User.objects.create_user(username="signal_user_1", password="x")

        assert CustomerProfile.objects.filter(user=user).exists()

    def test_profile_not_duplicated_on_user_update(self):
        User = get_user_model()
        user = User.objects.create_user(username="signal_user_2", password="x")

        assert CustomerProfile.objects.filter(user=user).count() == 1

        user.first_name = "Updated"
        user.save()

        assert CustomerProfile.objects.filter(user=user).count() == 1

    def test_idempotent_creation_check(self):
        User = get_user_model()
        user = User.objects.create_user(username="signal_user_3", password="x")

        # Ensure profile exists
        profile = CustomerProfile.objects.get(user=user)
        assert profile is not None

        # Simulate another post_save call by saving the user again
        user.save()

        # Still only one profile
        assert CustomerProfile.objects.filter(user=user).count() == 1
