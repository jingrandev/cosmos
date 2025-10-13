from django.db import models
from django.db import transaction
from django.utils import timezone

from core.db.querysets import AllQuerySet
from core.db.querysets import SoftDeleteQuerySet


class ActiveManager(models.Manager):
    """
    Manager that only returns non-deleted records
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def bulk_create(  # noqa: PLR0913
        self,
        objs,
        *,
        batch_size=None,
        ignore_conflicts=False,
        update_conflicts=False,
        update_fields=None,
        unique_fields=None,
    ):
        """
        Bulk create method that ensures is_deleted is False
        """
        for obj in objs:
            obj.is_deleted = False
        return super().bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )


class AllObjectsManager(models.Manager):
    """
    Manager that returns all records, including deleted ones
    """

    def get_queryset(self):
        return AllQuerySet(self.model, using=self._db)

    def deleted(self):
        """Return only deleted records"""
        return self.get_queryset().filter(is_deleted=True)

    @transaction.atomic
    def bulk_restore(self, objs, batch_size=None):
        """
        Bulk restore soft-deleted objects
        """
        if not objs:
            return 0

        now = timezone.now()
        for obj in objs:
            obj.is_deleted = False
            obj.deleted_at = None
            obj.updated_at = now

        return self.bulk_update(
            objs,
            ["is_deleted", "deleted_at", "updated_at"],
            batch_size=batch_size,
        )
