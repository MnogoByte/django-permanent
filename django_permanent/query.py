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
        qs = self.get_unpatched()
        obj, created = qs.get_or_create(**kwargs)
        if isinstance(obj, dict):
            geter, seter = obj.get, obj.__setitem__
        else:
            geter, seter = partial(getattr, obj), partial(setattr, obj)

        if not created and geter(settings.FIELD, True):
            seter(settings.FIELD, settings.FIELD_DEFAULT)
            self.model.all_objects.filter(id=geter('id')).update(**{settings.FIELD: settings.FIELD_DEFAULT})
        return obj

    def restore(self):
        return self.get_unpatched().update(**{settings.FIELD: settings.FIELD_DEFAULT})

    def values(self, *fields):
        klass = type('CustomValuesQuerySet', (self.__class__, ValuesQuerySet,), {})
        return self._clone(klass=klass, setup=True, _fields=fields)

    # I don't like the bottom code, but most of operations during QuerySet cloning Django do outside of __init___,
    # so I couldn't find a proper solution to provide transparency of restoration. If you does mail me please.

    def get_unpatched(self):
        qs = self._clone()
        qs._unpatch()
        return qs

    def _clone(self, **kwargs):
        c = super(PermanentQuerySet, self)._clone(**kwargs)
        # We need clones stay unpatched
        if getattr(self, '_unpatched', False):
            c._unpatched = True
            c._unpatch()
        return c

    def _patch(self, q_object):
        self.query.add_q(q_object)

    def _unpatch(self):
        self._unpatched = True
        if not self.query.where.children:
            return
        condition = self.query.where.children[0]

        if DJANGO_VERSION > (1, 7, -1):  # 1.7 changes query building mechanism
            is_patched = hasattr(condition, 'lhs') and condition.lhs.source.name == settings.FIELD
        else:
            is_patched = isinstance(condition, tuple) and condition[0].col == settings.FIELD

        if is_patched:
            del self.query.where.children[0]


class NonDeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(NonDeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self._patch(Q(**{settings.FIELD: settings.FIELD_DEFAULT}))


class DeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(DeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self._patch(~Q(**{settings.FIELD: settings.FIELD_DEFAULT}))
