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
    qs_class = BasePermanentQuerySet

    def get_queryset(self) -> BasePermanentQuerySet[T]:
        return self.qs_class(self.model, using=self._db)

    def get_restore_or_create(self, *args, **kwargs):
        return self.get_queryset().get_restore_or_create(*args, **kwargs)

    def restore(self, *args, **kwargs):
        return self.get_queryset().restore(*args, **kwargs)


class NonDeletedManager_(BasePermanentManager[T]):
    qs_class = NonDeletedQuerySet


NonDeletedManager = NonDeletedManager_.from_queryset(NonDeletedQuerySet)


class AllObjectsManager_(BasePermanentManager[T]):
    qs_class = PermanentQuerySet


AllObjectsManager = AllObjectsManager_.from_queryset(PermanentQuerySet)


class DeletedObjectsManager_(BasePermanentManager[T]):
    qs_class = DeletedQuerySet


DeletedObjectsManager = DeletedObjectsManager_.from_queryset(DeletedQuerySet)

QS = TypeVar("QS", bound=models.QuerySet)

CLS = TypeVar("CLS", bound=models.Manager)


def MultiPassThroughManager(
    cls: type[QS],
    base_cls: type[BasePermanentQuerySet],
) -> "type[QS]":
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (cls, base_cls), {})
    result = result_class.as_manager()

    globals()[name] = result_class

    return result


def MultiPassThroughQuerySet(
    cls: type[QS],
    base_cls: type[BasePermanentQuerySet],
) -> "type[QS]":
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (cls, base_cls), {})

    return result_class


def merge_manager_queryset(manager: CLS, base_cls: type) -> CLS:
    cls = manager._queryset_class
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (cls, base_cls), {})
    manager._queryset_class = result_class
    return manager
