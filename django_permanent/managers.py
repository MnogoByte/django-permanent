from django.db.models import Manager as Manager


def QuerySetManager(qs):

    class QuerySetManager(Manager):
        qs_class = qs

        def get_queryset(self):
            return self.qs_class(self.model, using=self._db)

    return QuerySetManager()


def MultiPassThroughManager(*classes):
    from model_utils.managers import PassThroughManager
    name = "".join([cls.__name__ for cls in classes])
    return PassThroughManager.for_queryset_class(type(name, classes, {}))()
