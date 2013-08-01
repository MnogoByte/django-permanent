from django.db.models import Manager as Manager

from . import PERMANENT_FIELD
from .query import PermanentQuerySet


class PermanentManager(Manager):
    def get_query_set(self):
        return PermanentQuerySet(self.model, using=self._db).filter(**{PERMANENT_FIELD: None})


class DeletedManager(Manager):
    def get_query_set(self):
        return PermanentQuerySet(self.model, using=self._db).exclude(**{PERMANENT_FIELD: None})
