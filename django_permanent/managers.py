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

    Merges the underlying classes of the original queryset with the base class
    """
    cls = manager._queryset_class
    name = "".join([cls.__name__, base_cls.__name__])
    result_class = type(name, (base_cls, cls), {})
    return manager.__class__.from_queryset(result_class)()


def MakePermanentManagers(manager: CLS) -> tuple[CLS, CLS, CLS]:
    """Given a Manager Instance, returns `objects`, `all_objects` and `deleted_objects` managers.

    Usage:

    class BaseModel(PermanentModel):
        objects, all_objects, deleted_objects = MakePermanentManagers(QuerySet.as_manager())
    """
    return (
        merge_queryset(manager, NonDeletedQuerySet),
        merge_queryset(manager, PermanentQuerySet),
        merge_queryset(manager, DeletedQuerySet),
    )
