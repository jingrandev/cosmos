from collections.abc import Sequence
from typing import Any

from django.contrib.auth import get_user_model
from factory import Faker
from factory import LazyAttribute
from factory import post_generation
from factory.django import DjangoModelFactory
from faker import Faker as FakerFactory

fake = FakerFactory()

User = get_user_model()


class UserFactory(DjangoModelFactory[User]):
    username = LazyAttribute(lambda _: f"{fake.user_name()}")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(lambda obj: f"{obj.username}@{fake.domain_name()}")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results and not cls._meta.skip_postgeneration_save:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()

    class Meta:
        model = User

        django_get_or_create = ["username"]
