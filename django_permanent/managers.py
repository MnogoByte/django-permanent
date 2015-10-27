from django.db.models import Manager


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
    name = "".join([cls.__name__ for cls in classes])
    return type(name, classes, {}).as_manager()
