from model_utils.managers import PassThroughManager

from django.db.models import Manager as Manager

from .query import PermanentQuerySet, NonDeletedQuerySet, DeletedQuerySet


def get_objects(cls):
    class QuerySet(cls, NonDeletedQuerySet):
        pass
    return PassThroughManager.for_queryset_class(QuerySet)()


def get_deleted_objects(cls):
    class QuerySet(cls, DeletedQuerySet):
        pass
    return PassThroughManager.for_queryset_class(QuerySet)()


def get_any_objects(cls):
    class QuerySet(cls, PermanentQuerySet):
        pass
    return PassThroughManager.for_queryset_class(QuerySet)()
