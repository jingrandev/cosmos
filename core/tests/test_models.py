# ruff: noqa: PLR2004
from datetime import UTC

from django.test import TestCase
from django.utils import timezone

from .models import DummyModel
from .models import RegularModel


class TestBaseModel(TestCase):
    """Test cases for regular BaseModel functionality"""

    def setUp(self):
        """Set up test data"""
        self.test_obj = RegularModel.objects.create(name="test")
        self.bulk_objects = [RegularModel(name=f"bulk_{i}") for i in range(3)]
        RegularModel.objects.bulk_create(self.bulk_objects)

    def test_default_fields(self):
        """Test that default fields are set correctly"""
        # Test created_at is set
        assert self.test_obj.created_at is not None
        assert timezone.is_aware(self.test_obj.created_at)

        # Test updated_at is set
        assert self.test_obj.updated_at is not None
        assert timezone.is_aware(self.test_obj.updated_at)

    def test_update_timestamps(self):
        """Test that updated_at is updated on save"""
        old_updated_at = self.test_obj.updated_at
        self.test_obj.name = "updated"
        self.test_obj.save()

        assert self.test_obj.updated_at > old_updated_at
        assert self.test_obj.name == "updated"

    def test_timezone_awareness(self):
        """Test that all datetime fields are timezone-aware"""
        obj = RegularModel.objects.create(name="tz_test")

        assert timezone.is_aware(obj.created_at)
        assert timezone.is_aware(obj.updated_at)

        # Test timezone conversion
        local_time = obj.created_at
        utc_time = local_time.astimezone(UTC)
        assert local_time.replace(tzinfo=None) == utc_time.replace(
            tzinfo=None,
        ) + timezone.get_default_timezone().utcoffset(None)


class TestSoftDeleteBaseModel(TestCase):
    """Test cases for SoftDeleteBaseModel functionality"""

    def setUp(self):
        """Set up test data"""
        self.test_obj = DummyModel.objects.create(name="test")
        self.bulk_objects = [DummyModel(name=f"bulk_{i}") for i in range(3)]
        DummyModel.objects.bulk_create(self.bulk_objects)

    def test_default_fields(self):
        """Test that default fields are set correctly"""
        # Test created_at is set
        assert self.test_obj.created_at is not None
        assert timezone.is_aware(self.test_obj.created_at)

        # Test updated_at is set
        assert self.test_obj.updated_at is not None
        assert timezone.is_aware(self.test_obj.updated_at)

        # Test is_deleted defaults to False
        assert not self.test_obj.is_deleted

    def test_update_timestamps(self):
        """Test that updated_at is updated on save"""
        old_updated_at = self.test_obj.updated_at
        self.test_obj.name = "updated"
        self.test_obj.save()

        assert self.test_obj.updated_at > old_updated_at
        assert self.test_obj.name == "updated"

    def test_soft_delete(self):
        """Test soft deletion functionality"""
        # Test soft delete
        self.test_obj.delete()
        assert self.test_obj.is_deleted

        # Test object still exists in database
        assert DummyModel.all_objects.filter(pk=self.test_obj.pk).exists()

        # Test object is not in active queryset
        assert not DummyModel.objects.filter(pk=self.test_obj.pk).exists()

    def test_hard_delete(self):
        """Test hard deletion functionality"""
        pk = self.test_obj.pk
        self.test_obj.hard_delete()

        # Test object is completely removed
        assert not DummyModel.all_objects.filter(pk=pk).exists()

    def test_restore(self):
        """Test restore functionality"""
        self.test_obj.delete()
        assert self.test_obj.is_deleted

        self.test_obj.restore()
        assert not self.test_obj.is_deleted
        assert DummyModel.objects.filter(pk=self.test_obj.pk).exists()

    def test_bulk_operations(self):
        """Test bulk operations"""
        # Test bulk soft delete
        DummyModel.objects.all().delete()
        assert DummyModel.objects.count() == 0
        assert DummyModel.all_objects.count() == 4  # including the single test_obj

        # Test bulk restore
        DummyModel.all_objects.bulk_restore(DummyModel.all_objects.deleted().all())
        assert DummyModel.objects.count() == 4

        # Test bulk create with timestamps
        bulk_created = DummyModel.objects.bulk_create(
            [
                DummyModel(name="bulk_new_1"),
                DummyModel(name="bulk_new_2"),
            ],
        )
        for obj in bulk_created:
            assert obj.created_at is not None
            assert obj.updated_at is not None
            assert timezone.is_aware(obj.created_at)
            assert timezone.is_aware(obj.updated_at)

        # Test bulk update
        now = timezone.now()
        objs = list(DummyModel.objects.all())
        for obj in objs:
            obj.name = f"updated_{obj.pk}"
        DummyModel.objects.bulk_update(objs, ["name"])
        for obj in DummyModel.objects.all():
            assert obj.name.startswith("updated_")
            assert obj.updated_at > now

    def test_manager_querysets(self):
        """Test custom manager and queryset functionality"""
        # First, let's clean up any existing objects
        DummyModel.all_objects.all().delete()

        # Create a mix of active and deleted objects
        DummyModel.objects.create(name="active1")
        obj2 = DummyModel.objects.create(name="active2")
        obj2.delete()  # This one will be soft-deleted

        # Now we should have:
        # - 1 active object (obj1)
        # - 1 soft-deleted object (obj2)

        # Test active manager (default)
        assert DummyModel.objects.count() == 1  # only obj1

        # Test all_objects manager
        assert DummyModel.all_objects.count() == 2

        # Test deleted records
        assert DummyModel.all_objects.deleted().count() == 1
