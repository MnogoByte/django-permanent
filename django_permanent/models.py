from django.db import models, router
from django.utils.module_loading import import_by_path

from django_permanent import settings
from .deletion import PermanentCollector
from .query import NonDeletedQuerySet, DeletedQuerySet, PermanentQuerySet
from .managers import QuerySetManager


class PermanentModel(models.Model):
    objects = QuerySetManager(NonDeletedQuerySet)
    deleted_objects = QuerySetManager(DeletedQuerySet)
    all_objects = QuerySetManager(PermanentQuerySet)
    _base_manager = objects

    class Meta:
        abstract = True

    def delete(self, using=None, force=None):
        if force:
            super(PermanentModel, self).delete(using=using)

        else:
            using = using or router.db_for_write(self.__class__, instance=self)
            assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

            collector = PermanentCollector(using=using)
            collector.collect([self])
            collector.delete()

    delete.alters_data = True

    def restore(self):
        setattr(self, settings.FIELD, settings.FIELD_DEFAULT)
        self.save()


field = import_by_path(settings.FIELD_CLASS)
PermanentModel.add_to_class(settings.FIELD, field(**settings.FIELD_KWARGS))
