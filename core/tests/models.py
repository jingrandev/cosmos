from django.db import models

from core.db.models import BaseModel
from core.db.models import SoftDeleteBaseModel


class DummyModel(SoftDeleteBaseModel):
    """A test model that inherits from SoftDeleteBaseModel"""

    name = models.CharField(max_length=100)


class RegularModel(BaseModel):
    """A test model that inherits from regular BaseModel without soft delete"""

    name = models.CharField(max_length=100)


class UniqueFieldModel(SoftDeleteBaseModel):
    """Test model with unique fields that form composite unique constraints with id_copy"""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    code = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "id_copy"], name="unique_name_id_copy"),
            models.UniqueConstraint(fields=["email", "id_copy"], name="unique_email_id_copy"),
        ]


class MultiUniqueFieldModel(SoftDeleteBaseModel):
    """Test model with multiple unique fields that form a composite unique constraint with id_copy"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "code", "id_copy"], name="unique_name_code_id_copy"),
        ]


class CustomPKModel(SoftDeleteBaseModel):
    """Test model with custom primary key type"""

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code", "id_copy"], name="unique_code_id_copy"),
        ]
