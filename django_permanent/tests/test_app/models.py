from django.db import models
from django.db.models import Model
from django_permanent.models import PermanentModel
from django_permanent.managers import MultiPassThroughManager
from django_permanent.query import DeletedQuerySet, PermanentQuerySet, NonDeletedQuerySet
from django_permanent.tests.cond import model_utils_installed


class BaseTestModel(Model):

    class Meta():
        abstract = True

    def __unicode__(self):
        return unicode(self.pk)


class MyPermanentModel(BaseTestModel, PermanentModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    pass


class RemovableDepended(BaseTestModel):
    dependence = models.ForeignKey(MyPermanentModel)


class NonRemovableDepended(BaseTestModel, PermanentModel):
    dependence = models.ForeignKey(MyPermanentModel, on_delete=models.DO_NOTHING)


class PermanentDepended(BaseTestModel, PermanentModel):
    dependence = models.ForeignKey(MyPermanentModel)


class M2MFrom(BaseTestModel):
    pass


class PermanentM2MThrough(PermanentModel):
    m2m_from = models.ForeignKey('M2MFrom')
    m2m_to = models.ForeignKey('M2MTo')


class M2MTo(BaseTestModel):
    m2m_from = models.ManyToManyField('M2MFrom', through=PermanentM2MThrough)


class MyPermanentQuerySet(PermanentQuerySet):
    def test(self):
        pass


class MyPermanentModelWithManager(BaseTestModel, PermanentModel):
    name = models.CharField(max_length=255, blank=True, null=True)

    objects = MultiPassThroughManager(MyPermanentQuerySet, NonDeletedQuerySet)
    deleted_objects = MultiPassThroughManager(MyPermanentQuerySet, DeletedQuerySet)
    any_objects = MultiPassThroughManager(MyPermanentQuerySet, PermanentQuerySet)


if model_utils_installed:

    class TestQS(object):
        def test(self):
            return "ok"

    class CustomQsPermanent(BaseTestModel, PermanentModel):
        objects = MultiPassThroughManager(TestQS, DeletedQuerySet)
