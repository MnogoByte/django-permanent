from django.db.models import Manager as Manager
from django_permanent import settings


def patch_many_related_manager(manager):
    from django_permanent.models import PermanentModel
    if manager.__class__.__name__ == 'ManyRelatedManager' and issubclass(manager.through, PermanentModel):
        manager.core_filters['%s__%s' % (manager.source_field.related_query_name(), settings.FIELD)] = None


def QuerySetManager(qs):

    class QuerySetManager(Manager):
        qs_class = qs

        def get_queryset(self):
            patch_many_related_manager(self)
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


def get_queryset(self):
    patch_many_related_manager(self)
    return self.old_get_queryset()


Manager.get_queryset, Manager.old_get_queryset = get_queryset, Manager.get_queryset
