from model_utils.managers import PassThroughManager

from django.db import models, router

from . import PERMANENT_FIELD
from .deletion import PermanentCollector
from .query import NonDeletedQuerySet, DeletedQuerySet, PermanentQuerySet


class PermanentModel(models.Model):
    objects = PassThroughManager.for_queryset_class(NonDeletedQuerySet)()
    deleted_objects = PassThroughManager.for_queryset_class(DeletedQuerySet)()
    all_objects = PassThroughManager.for_queryset_class(PermanentQuerySet)()

    class Meta:
        abstract = True

    def delete(self, using=None, force=None):
        if force:
            super(PermanentModel, self).delete(using=using)

        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

        collector = PermanentCollector(using=using)
        collector.collect([self])
        collector.delete()

    delete.alters_data = True

    def restore(self):
        setattr(self, PERMANENT_FIELD, None)
        self.save()


PermanentModel.add_to_class(PERMANENT_FIELD, models.DateTimeField(blank=True, null=True, editable=False))
