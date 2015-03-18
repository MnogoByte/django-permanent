from functools import partial

from django.db.models.query import QuerySet, ValuesQuerySet
from django.db.models.query_utils import Q

from django_permanent import settings
from django import VERSION as DJANGO_VERSION


class PermanentQuerySet(QuerySet):
    def create(self, **kwargs):
        if self.model.Permanent.restore_on_create:
            return self.get_restore_or_create(**kwargs)
        return super(PermanentQuerySet, self).create(**kwargs)

    def get_restore_or_create(self, **kwargs):
        obj, created = QuerySet(self.model).get_or_create(**kwargs)
        if isinstance(obj, dict):
            geter, seter = obj.get, obj.__setitem__
        else:
            geter, seter = partial(getattr, obj), partial(setattr, obj)

        if not created and geter(settings.FIELD, True):
            seter(settings.FIELD, settings.FIELD_DEFAULT)
            self.model.all_objects.filter(id=geter('id')).update(**{settings.FIELD: settings.FIELD_DEFAULT})
        return obj

    def restore(self):
        return QuerySet(self.model).update(**{settings.FIELD: settings.FIELD_DEFAULT})

    def values(self, *fields):
        klass = type('CustomValuesQuerySet', (self.__class__, ValuesQuerySet,), {})
        return self._clone(klass=klass, setup=True, _fields=fields)


class NonDeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(NonDeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self.query.add_q(Q(**{settings.FIELD: settings.FIELD_DEFAULT}))


class DeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(DeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self.query.add_q(~Q(**{settings.FIELD: settings.FIELD_DEFAULT}))
