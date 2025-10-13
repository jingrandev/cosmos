from django.db.models import F
from django.db.models.query import QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    """
    QuerySet for soft-deleted records management
    """

    def delete(self):
        """Soft delete all records in the queryset"""
        return self.update(
            is_deleted=True,
            id_copy=F("pk"),
            deleted_at=timezone.now(),
            updated_at=timezone.now(),
        )

    def hard_delete(self):
        """Permanently delete all records in the queryset"""
        return super().delete()

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
        Override bulk_create to ensure created_at and updated_at are set
        """
        now = timezone.now()
        for obj in objs:
            if not getattr(obj, "created_at", None):
                obj.created_at = now
            if not getattr(obj, "updated_at", None):
                obj.updated_at = now
        return super().bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )

    def bulk_update(self, objs, fields, batch_size=None):
        """
        Override bulk_update to ensure updated_at is included
        """
        now = timezone.now()
        for obj in objs:
            obj.updated_at = now

        if "updated_at" not in fields:
            fields = [*fields, "updated_at"]

        return super().bulk_update(objs, fields, batch_size=batch_size)


class AllQuerySet(QuerySet):
    """
    QuerySet for all records management
    """

    def restore(self):
        """Restore all soft-deleted records in the queryset"""
        return self.update(is_deleted=False, id_copy="", deleted_at=None, updated_at=timezone.now())
