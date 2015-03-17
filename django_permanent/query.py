from functools import partial

from django.db.models.query import QuerySet, ValuesQuerySet
from django.db.models.query_utils import Q

from django_permanent import settings
from .deletion import PermanentCollector
from django import VERSION as DJANGO_VERSION


class PermanentQuerySet(QuerySet):
    def get_restore_or_create(self, **kwargs):
        qs = self.get_unpatched()
        obj, created = qs.get_or_create(**kwargs)
        if isinstance(obj, dict):
            geter, seter = obj.get, obj.__setitem__
        else:
            geter, seter = partial(getattr, obj), partial(setattr, obj)

        if not created and geter(settings.FIELD, True):
            seter(settings.FIELD, settings.FIELD_DEFAULT)
            self.model.objects.filter(id=geter('id')).update(**{settings.FIELD:settings.FIELD_DEFAULT})
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
    delete.alters_data = True

    def restore(self):
        return self.get_unpatched().update(**{settings.FIELD: settings.FIELD_DEFAULT})

    def values(self, *fields):
        klass = type('CustomValuesQuerySet', (self.__class__, ValuesQuerySet,), {})
        return self._clone(klass=klass, setup=True, _fields=fields)

    def get_unpatched(self):
        qs = self._clone(PermanentQuerySet)
        condition = qs.query.where.children[0]

        if DJANGO_VERSION > (1, 7, -1):  # 1.7 changes query building mechanism
            is_patched = hasattr(condition, 'lhs') and condition.lhs.source.name == settings.FIELD
        else:
            is_patched = isinstance(condition, tuple) and condition[0].col == settings.FIELD

        if is_patched:
            del qs.query.where.children[0]
        return qs


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
