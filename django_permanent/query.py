from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q

from . import PERMANENT_FIELD
from .deletion import PermanentCollector


class PermanentQuerySet(QuerySet):
    def get_restore_or_create(self, **kwargs):
        try:
            obj = self.get(**kwargs)
        except ObjectDoesNotExist:
            return self.create(**kwargs)
        if getattr(obj, PERMANENT_FIELD):
            setattr(obj, PERMANENT_FIELD, None)
            obj.save(update_fields=[PERMANENT_FIELD])
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


class NonDeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(NonDeletedQuerySet, self).__init__(*args, **kwargs)
        self.query.add_q(Q(**{PERMANENT_FIELD: None}))


class DeletedQuerySet(PermanentQuerySet):
    def __init__(self, *args, **kwargs):
        super(DeletedQuerySet, self).__init__(*args, **kwargs)
        self.query.add_q(~Q(**{PERMANENT_FIELD: None}))
