from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from core.db.managers import ActiveManager
from core.db.managers import AllObjectsManager


class IdCopyField(models.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault("verbose_name", _("ID Copy"))
        kwargs.setdefault("blank", True)
        kwargs.setdefault("editable", False)
        kwargs.setdefault("help_text", _("Copy of the primary key"))
        kwargs.setdefault("max_length", 255)
        super().__init__(**kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        default_auto_field = import_string(getattr(settings, "DEFAULT_AUTO_FIELD", "django.db.models.AutoField"))
        pk_field = default_auto_field()
        if getattr(cls._meta, "pk", None):
            pk_field = cls._meta.pk
        else:
            app_label = cls._meta.app_label
            if app_label:
                app_config = apps.get_app_config(app_label)
                app_auto_field = import_string(app_config.default_auto_field)
                pk_field = app_auto_field()

        if getattr(pk_field, "max_length", None):
            self.max_length = pk_field.max_length
        elif isinstance(pk_field, models.IntegerField):
            self.max_length = 20
        elif isinstance(pk_field, models.UUIDField):
            self.max_length = 36

        super().contribute_to_class(cls, name, **kwargs)


class SoftDeleteMixin(models.Model):
    """
    Mixin that provides soft deletion functionality for models.

    Fields:
        is_deleted: Soft deletion flag
        deleted_at: Timestamp when the record was deleted
        id_copy: Copy of the primary key
    """

    is_deleted = models.BooleanField(
        verbose_name=_("Deleted"),
        default=False,
        help_text=_("Whether this record is deleted"),
    )
    deleted_at = models.DateTimeField(
        verbose_name=_("Deleted at"),
        null=True,
        help_text=_("When this record was deleted"),
    )

    id_copy = IdCopyField()

    objects = ActiveManager()  # Default manager, only returns non-deleted records
    all_objects = AllObjectsManager()  # Returns all records including deleted ones

    class Meta:
        abstract = True

    def delete(self, *, using=None, keep_parents: bool = False):
        """
        Soft delete the model instance by setting is_deleted=True and deleted_at to current time.
        To perform a hard delete, use Model.objects.filter(pk=id).delete()
        """
        if self.id_copy == "":
            self.id_copy = str(self.pk)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, *, using=None, keep_parents: bool = False):
        """
        Permanently delete the model instance from the database
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self, *, using=None):
        """
        Restore a soft-deleted instance
        """
        self.is_deleted = False
        self.deleted_at = None
        self.id_copy = ""
        self.save(using=using)
