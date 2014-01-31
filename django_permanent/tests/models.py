from django.db import models
from django.db.models import Model
from django_permanent.models import PermanentModel


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
