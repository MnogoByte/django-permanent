from typing import TYPE_CHECKING, cast

from django.db import models
from django.db.models import Model

from django_permanent.managers import MakeAllObjects, MakeDeletedManager, MakeObjects
from django_permanent.models import PermanentModel
from django_permanent.query import (
    BasePermanentQuerySet,
    DeletedQuerySet,
    NonDeletedQuerySet,
    PermanentQuerySet,
    T,
)


class BaseModel(PermanentModel):
    pass


class PlainQuerySet(models.QuerySet):
    pass


class PlainModel(models.Model):
    """Plain model but with custom queryset created in various manners"""

    from_queryset_manager = models.Manager.from_queryset(PlainQuerySet)()


class CustomManager(models.Manager["PassthroughModel"]):
    ...


class CustomQuerySet(BasePermanentQuerySet):
    pass


class CustomQuerySetDeleted(DeletedQuerySet["PassthroughModel"]):
    pass


class CustomQuerySetPermanent(PermanentQuerySet["PassthroughModel"]):
    pass


from typing import TypeVar

QST = CustomQuerySet.as_manager()


class PassthroughModel(PermanentModel):
    a_objects = MakeObjects(CustomQuerySet.as_manager())
    b_objects = MakeDeletedManager(CustomManager())
    c_objects = MakeAllObjects(models.Manager.from_queryset(CustomQuerySet)())


PassthroughModel.a_objects.all().get_restore_or_create
if TYPE_CHECKING:
    reveal_type(PassthroughModel.a_objects.all())
    reveal_type(PassthroughModel.b_objects.all())
    reveal_type(PassthroughModel.c_objects.all())
    reveal_type(PassthroughModel.a_objects.all())
    # pass

    #### Type checking plain models
    reveal_type(PlainModel.objects.all())
    reveal_type(PlainModel.from_queryset_manager.all())

    ## Type checking a plain permanent tracked model
    #
    reveal_type(BaseModel.objects.all())
    reveal_type(BaseModel.objects)
    reveal_type(BaseModel.objects.all().get_restore_or_create)
    reveal_type(BaseModel.objects.get_restore_or_create)

    reveal_type(BaseModel.all_objects.all())
    reveal_type(BaseModel.all_objects)

    reveal_type(BaseModel.deleted_objects.all())
    reveal_type(BaseModel.deleted_objects)
