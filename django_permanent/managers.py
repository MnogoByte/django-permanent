from django.db.models import Manager
from django.db.models.fields import related
from django_permanent import settings


def QuerySetManager(qs):

    class QuerySetManager(Manager):
        qs_class = qs

        def get_queryset(self):
            return self.qs_class(self.model, using=self._db)

        def get_restore_or_create(self, *args, **kwargs):
            return self.get_queryset().get_restore_or_create(*args, **kwargs)

        def restore(self, *args, **kwargs):
            return self.get_queryset().restore(*args, **kwargs)

    return QuerySetManager()


def MultiPassThroughManager(*classes):
    from model_utils.managers import PassThroughManager
    name = "".join([cls.__name__ for cls in classes])
    return PassThroughManager.for_queryset_class(type(name, classes, {}))()


class PermanentMixIn(object):
    def get_queryset(self, *args, **kwargs):
        from django_permanent.models import PermanentModel
        if issubclass(self.through, PermanentModel):
            self.core_filters['%s__%s' % (self.source_field.related_query_name(), settings.FIELD)] = settings.FIELD_DEFAULT
        return super(PermanentMixIn, self).get_queryset(*args, **kwargs)

    def get_prefetch_queryset(self, *args, **kwargs):
        from django_permanent.models import PermanentModel
        result = super(PermanentMixIn, self).get_prefetch_queryset(*args, **kwargs)
        if issubclass(self.through, PermanentModel):
            join_table = self.through._meta.db_table
            return (result[0].extra(where={"%s.%s" % (join_table, settings.FIELD): settings.FIELD_DEFAULT}),) + result[1:]
        return result


def mix_into_result(*classes):
    def dec1(func):
        def dec2(*args, **kwargs):
            klass = func(*args, **kwargs)
            bases = classes + (klass, )
            name = "".join([klass.__name__ for klass in bases])
            return type(name, bases, {})
        return dec2
    return dec1


related.create_many_related_manager = mix_into_result(PermanentMixIn)(related.create_many_related_manager)
