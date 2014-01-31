
from django.db.models import Manager as Manager

from .query import PermanentQuerySet, NonDeletedQuerySet, DeletedQuerySet


class QuerySetManager(Manager):
    qs_class = None

    def __init__(self, qs_class):
        self.qs_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_queryset(self):
        return self.qs_class(self.model, using=self._db)


def MultiPassThroughManager(*classes):
    from model_utils.managers import PassThroughManager
    name = "".join([cls.__name__ for cls in classes])
    return PassThroughManager.for_queryset_class(type(name, classes, {}))()
