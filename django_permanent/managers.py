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


def clone_manager_with_merged_queryset(
    manager: CLS, permanent_queryset_cls: type[BasePermanentQuerySet]
) -> CLS:
    """Creates a clone of the Manager from the subclass of querysets

    Merges the underlying manager's queryset with the input permanent queryset cls.
    """
    original_queryset_cls = manager._queryset_class
    new_queryset_cls_name = "".join(
        [original_queryset_cls.__name__, permanent_queryset_cls.__name__]
    )

    # Merge the underlying queryset classes
    queryset_class = type(
        new_queryset_cls_name, (permanent_queryset_cls, original_queryset_cls), {}
    )

    # Create a new manager (but from the merged queryset class)
    # And give it the same name as before
    class_name = f"{manager.__class__.__name__}"

    # It is important to give it the same name as before for MyPy dynamic lookup of type info
    full_class = manager.__class__.from_queryset(
        queryset_class,
        # .... setting the class name to Manager makes the class lookup possible in Mypy.
        class_name=class_name,
    )
    full_class.is_django_permanent_patched = True

    instance = full_class()
    return instance


def MakePermanentManagers(manager: CLS) -> tuple[CLS, CLS, CLS]:
    """Given a Manager Instance, returns `objects`, `all_objects` and `deleted_objects` managers.

    Usage:

    class BaseModel(PermanentModel):
        objects, all_objects, deleted_objects = MakePermanentManagers(QuerySet.as_manager())
    """
    return (
        clone_manager_with_merged_queryset(manager, NonDeletedQuerySet),
        clone_manager_with_merged_queryset(manager, PermanentQuerySet),
        clone_manager_with_merged_queryset(manager, DeletedQuerySet),
    )
