from django.db.models.query import QuerySet

from . import PERMANENT_FIELD
from .deletion import PermanentCollector


class PermanentQuerySet(QuerySet):
    def all_with_deleted(self):
        return self.all()

    def not_deleted_only(self):
        return self.filter(**{PERMANENT_FIELD: None})

    def deleted_only(self):
        return self.exclude(**{PERMANENT_FIELD: None})

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


class PermanentQuerySetByPK(PermanentQuerySet):
    def filter(self, **kwargs):
        if ('pk' in kwargs and
            self.query.where.children and
            len(self.query.where.children[0].children) == 1 and
            self.query.where.children[0].children[0][0].col == PERMANENT_FIELD):
                clone = self._clone()
                del clone.query.where.children[0]
                return clone.filter(**kwargs)
        return super(PermanentQuerySet, self).filter(**kwargs)


def permanent_queryset(qs):
    def func(*args, **kwargs):
        return qs(*args, **kwargs).not_deleted_only()
    return func


def deleted_queryset(qs):
    def func(*args, **kwargs):
        return qs(*args, **kwargs).deleted_only()
    return func
