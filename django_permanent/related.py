import django
from django.db.models.fields.related import ForeignObject

from . import settings
from .query import AllWhereNode, DeletedWhereNode


def get_extra_restriction_patch(func):
    def wrapper(self, where_class, alias, lhs):
        cond = func(self, where_class, alias, lhs)

        from .models import PermanentModel
        if not issubclass(self.model, PermanentModel) or issubclass(where_class, AllWhereNode):
            return cond

        if issubclass(where_class, DeletedWhereNode):
            cond = cond or ~where_class()
        else:
            cond = cond or where_class()

        if django.VERSION < (1, 8, 0):
            field = self.model._meta.get_field_by_name(settings.FIELD)[0]
        else:
            field = self.model._meta.get_field(settings.FIELD)

        if django.VERSION < (1, 7, 0):
            from django.db.models.sql.where import Constraint
            if settings.FIELD_DEFAULT is None:
                lookup = Constraint(lhs, settings.FIELD, field), 'isnull', True
            else:
                lookup = Constraint(lhs, alias, field), 'exact', settings.FIELD_DEFAULT

        else:
            if django.VERSION < (1, 8, 0):
                from django.db.models.sql.datastructures import Col
            else:
                from django.db.models.expressions import Col

            if settings.FIELD_DEFAULT is None:
                lookup = field.get_lookup('isnull')(Col(lhs, field, field), True)
            else:
                lookup = field.get_lookup('exact')(Col(lhs, field, field), settings.FIELD_DEFAULT)

        cond.add(lookup, 'AND')

        return cond
    return wrapper


ForeignObject.get_extra_restriction = get_extra_restriction_patch(ForeignObject.get_extra_restriction)


if django.VERSION > (1, 8, -1):
    if django.VERSION > (1, 9, 0):
        from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor as Descriptor
    else:
        from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor as Descriptor

    def get_queryset_patch(func):
        def wrapper(self, **hints):
            from .models import PermanentModel
            instance = hints.get('instance')
            if instance and isinstance(instance, PermanentModel) and getattr(instance, settings.FIELD):
                if django.VERSION < (1, 9, 0):
                    model = self.field.rel.to
                else:
                    model = self.field.remote_field.model
                if hasattr(model, 'all_objects'):
                    return model.all_objects
                return model.objects
            return func(self, **hints)
        return wrapper

    Descriptor.get_queryset = get_queryset_patch(Descriptor.get_queryset)
