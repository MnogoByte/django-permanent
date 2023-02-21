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


def MultiPassThroughManager(
    cls: type,
    base_cls: type[BasePermanentQuerySet],
) -> Any:
    """This manager fcatory is deprecated. Prefer MakePermanentManagers."""
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
    new_queryset_class_name = "".join(
        [original_queryset_cls.__name__, permanent_queryset_cls.__name__]
    )

    # Merge the underlying queryset classes
    new_queryset_class = type(
        new_queryset_class_name, (permanent_queryset_cls, original_queryset_cls), {}
    )

    # Create a new manager (but from the merged queryset class)
    # And give it the same name as before
    new_manager_class_name = f"{manager.__class__.__name__}"

    # It is important to give it the same name as before for MyPy dynamic lookup of type info
    new_manager_class = manager.__class__.from_queryset(
        new_queryset_class,
        # .... setting the class name to Manager makes the class lookup possible in Mypy.
        class_name=new_manager_class_name,
    )

    instance = new_manager_class()
    return instance


def MakePermanentManagers(manager: CLS) -> tuple[CLS, CLS, CLS]:
    """Given a Manager Instance, returns `objects`, `all_objects` and `deleted_objects` managers.

    NOTE: This is the preferred approach however; this isn't mypy-django-stubs compatible.
    mypy-django-stubs requires manager classes to be directly addressable / referenceable.
    As such, the run time created manager classes do not work.

    Usage:

    class BaseModel(PermanentModel):
        objects, all_objects, deleted_objects = MakePermanentManagers(QuerySet.as_manager())
    """
    return (
        clone_manager_with_merged_queryset(manager, NonDeletedQuerySet),
        clone_manager_with_merged_queryset(manager, PermanentQuerySet),
        clone_manager_with_merged_queryset(manager, DeletedQuerySet),
    )
