from typing import TYPE_CHECKING, ClassVar, Self

import django
from django.db import models, router
from django.db.models.deletion import Collector
from django.utils.module_loading import import_string

from django_permanent.query import BasePermanentQuerySet, NonDeletedQuerySet, lol

from . import settings
from .deletion import *  # NOQA
from .managers import (
    AllObjectsManager,
    BasePermanentManager,
    DeletedObjectsManager,
    MultiPassThroughManager,
    NonDeletedManager,
)
from .related import *  # NOQA
from .signals import post_restore, pre_restore


class PermanentModel(models.Model):
    objects: ClassVar[BasePermanentManager["Self"]] = NonDeletedManager()
    all_objects: ClassVar[BasePermanentManager["Self"]] = AllObjectsManager()
    deleted_objects: ClassVar[BasePermanentManager["Self"]] = DeletedObjectsManager()

    class Meta:
        abstract = True

        if django.VERSION >= (1, 10):
            default_manager_name = "objects"
            base_manager_name = "objects"

    class Permanent:
        restore_on_create = False

    def delete(self, using=None, force=False):
        using = using or router.db_for_write(self.__class__, instance=self)
        assert (
            self._get_pk_val() is not None
        ), "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name,
            self._meta.pk.attname,
        )
        collector = Collector(using=using)
        collector.collect([self])
        collector.delete(force=force)

    delete.alters_data = True  # type: ignore

    def restore(self):
        pre_restore.send(sender=self.__class__, instance=self)
        setattr(self, settings.FIELD, settings.FIELD_DEFAULT)
        self.save(update_fields=[settings.FIELD])
        post_restore.send(sender=self.__class__, instance=self)


field = import_string(settings.FIELD_CLASS)
PermanentModel.add_to_class(settings.FIELD, field(**settings.FIELD_KWARGS))


if TYPE_CHECKING:

    class OtherModelQuerySet(models.QuerySet["OtherModel"]):
        def something(self) -> "Self":
            return self

        def add(self) -> "int":
            return 1

    M = models.Manager.from_queryset(OtherModelQuerySet)

    class OtherModel(PermanentModel):
        # lol_objects =OtherModelQuerySet.as_manager()
        lol_objects = M()
        rofl = MultiPassThroughManager(OtherModelQuerySet, NonDeletedQuerySet)

    reveal_type(OtherModel.lol_objects.something())
    reveal_type(OtherModel.lol_objects.add())
    reveal_type(OtherModel.lol_objects)

    from django.db import models

    class MyQuerySet(models.QuerySet):
        ...

    class MyModel(models.Model):
        objects = MyQuerySet.as_manager()

    reveal_type(
        MyModel.objects
    )  # N: Revealed type is "myapp.models.ManagerFromMyQuerySet[myapp.models.MyModel]"
