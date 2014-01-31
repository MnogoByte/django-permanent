from django.db import models
from django.db.models import Model
from django_permanent.models import PermanentModel
from django_permanent.managers import MultiPassThroughManager
from django_permanent.query import DeletedQuerySet
from .cond import model_utils_installed


class BaseTestModel(Model):

    class Meta():
        abstract = True

    def __unicode__(self):
        return unicode(self.pk)


class MyPermanentModel(BaseTestModel, PermanentModel):
    pass


class RemovableDepended(BaseTestModel):
    dependance = models.ForeignKey(MyPermanentModel)


class NonRemovableDepended(BaseTestModel):
    dependance = models.ForeignKey(MyPermanentModel, on_delete=models.DO_NOTHING)


class PermanentDepended(BaseTestModel, PermanentModel):
    dependance = models.ForeignKey(MyPermanentModel)


if model_utils_installed:

    class TestQS(object):
        def test(self):
            return "ok"

    class CustomQsPermanent(BaseTestModel, PermanentModel):
        objects = MultiPassThroughManager(TestQS, DeletedQuerySet)
