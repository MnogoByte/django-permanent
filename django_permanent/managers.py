from typing import Any, TypeVar

from django.db import models

from .query import (
    BasePermanentQuerySet,
    DeletedQuerySet,
    NonDeletedQuerySet,
    PermanentQuerySet,
    T,
)

CLS = TypeVar("CLS", bound=models.Manager)


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


def MultiPassThroughManager(
    cls: type,
    base_cls: type[BasePermanentQuerySet],
) -> Any:
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (cls, base_cls), {})
    result = result_class.as_manager()

    globals()[name] = result_class

    return result


def merge_queryset(manager: CLS, base_cls: type[BasePermanentQuerySet]) -> CLS:
    """Given a Manager, modifies the queryset of the manager with a dynamically created queryset.

    Merges the underlying classes of the original queryset with the base class.
    """
    cls = manager._queryset_class
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (base_cls, cls), {})
    manager._queryset_class = result_class
    return manager


def MakeDeletedObjects(manager: CLS) -> CLS:
    """Given a Manager, modifies the queryset to return only deleted objects.

    Usage:

    class BaseModel(PermanentModel):
        deleted_objects = MakeDeletedObjects(CustomQueryset.as_manager())
    """
    return merge_queryset(manager, DeletedQuerySet)


def MakeObjects(manager: CLS) -> CLS:
    """Given a Manager, modifies the queryset of the manager to return only non deleted objects.

    Usage:

    class BaseModel(PermanentModel):
        objects = MakeObjects(CustomQueryset.as_manager())
    """
    return merge_queryset(manager, NonDeletedQuerySet)


def MakeAllObjects(manager: CLS) -> CLS:
    """Given a Manager, modify the queryset to return all objects

    Usage:

    class BaseModel(PermanentModel):
        all_objects = MakeAllObjects(QuerySet.as_manager())
    """
    return merge_queryset(manager, PermanentQuerySet)
