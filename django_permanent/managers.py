from typing import TypeVar

from django.db import models

from .query import (
    BasePermanentQuerySet,
    DeletedQuerySet,
    NonDeletedQuerySet,
    PermanentQuerySet,
)

T = TypeVar("T", bound=models.Model)


class BasePermanentManager(models.Manager[T]):
    qs_class = NonDeletedQuerySet

    def get_queryset(self):
        return self.qs_class(self.model, using=self._db)

    def get_restore_or_create(self, *args, **kwargs):
        return self.get_queryset().get_restore_or_create(*args, **kwargs)

    def restore(self, *args, **kwargs):
        return self.get_queryset().restore(*args, **kwargs)


class NonDeletedManager(BasePermanentManager[T]):
    qs_class = NonDeletedQuerySet


class AllObjectsManager(BasePermanentManager[T]):
    qs_class = PermanentQuerySet


class DeletedObjectsManager(BasePermanentManager[T]):
    qs_class = DeletedQuerySet


QS = TypeVar("QS", bound=models.QuerySet)


def MultiPassThroughManager(
    cls: type[QS],
    base_cls: type[BasePermanentQuerySet],
) -> "type[QS]":
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (cls, base_cls), {})
    result = result_class.as_manager()

    globals()[name] = result_class

    return result
