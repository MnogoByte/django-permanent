from functools import partial

from django.db.models.query import QuerySet, ValuesQuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q

from . import PERMANENT_FIELD
from .deletion import PermanentCollector


class PermanentQuerySet(QuerySet):
    def get_restore_or_create(self, **kwargs):
        obj, created = self.get_or_create(**kwargs)

        if isinstance(obj, dict):
            geter, seter = obj.get, obj.__setitem__
        else:
            geter, seter = partial(getattr, obj), partial(setattr, obj)

        if not created and geter(PERMANENT_FIELD, True):
            seter(PERMANENT_FIELD, None)
            self.model.objects.filter(id=geter(obj, 'id')).update(removed=None)
        return obj

    def delete(self, force=False):
        """
        Deletes the records in the current QuerySet.
        """
        if force:
            return super(PermanentQuerySet, self).delete()

        assert self.query.can_filter(), \
                "Cannot use 'limit' or 'offset' with delete."

        del_query = self._clone()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        collector = PermanentCollector(using=del_query.db)
        collector.collect(del_query)
        collector.delete()

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None

    def restore(self):
        return self.update(**{PERMANENT_FIELD: None})

    def values(self, *fields):
        klass = type('CustomValuesQuerySet', (self.__class__, ValuesQuerySet,), {})
        return self._clone(klass=klass, setup=True, _fields=fields)


class NonDeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(NonDeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self.query.add_q(Q(**{PERMANENT_FIELD: None}))


class DeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(DeletedQuerySet, self).__init__(*args, **kwargs)
        if not self.query.where:
            self.query.add_q(~Q(**{PERMANENT_FIELD: None}))
