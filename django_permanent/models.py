from django.db import models, router
from django.utils.module_loading import import_by_path

from django_permanent import settings
from .deletion import *
from .query import NonDeletedQuerySet, DeletedQuerySet, PermanentQuerySet
from .managers import QuerySetManager


class PermanentModel(models.Model):
    objects = QuerySetManager(NonDeletedQuerySet)
    deleted_objects = QuerySetManager(DeletedQuerySet)
    all_objects = QuerySetManager(PermanentQuerySet)
    _base_manager = objects

    class Meta:
        abstract = True

    class Permanent:
        restore_on_create = False

    def restore(self):
        setattr(self, settings.FIELD, settings.FIELD_DEFAULT)
        self.save()


field = import_by_path(settings.FIELD_CLASS)
PermanentModel.add_to_class(settings.FIELD, field(**settings.FIELD_KWARGS))
