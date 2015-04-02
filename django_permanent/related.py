import django
from django.db.models.fields.related import ForeignObject
from django_permanent import settings


def get_extra_restriction_patch(func):
    def wrapper(self, where_class, alias, lhs):
        cond = func(self, where_class, alias, lhs)
        from .models import PermanentModel
        if issubclass(self.model, PermanentModel):
            cond = cond or where_class()
            field = self.model._meta.get_field_by_name(settings.FIELD)[0]

            if django.VERSION < (1, 7, 0):
                from django.db.models.sql.where import Constraint
                if settings.FIELD_DEFAULT is None:
                    lookup = Constraint(lhs, settings.FIELD, field), 'isnull', True
                else:
                    lookup = Constraint(lhs, alias, field), 'exact', None

            else:
                from django.db.models.sql.datastructures import Col
                if settings.FIELD_DEFAULT is None:
                    lookup = field.get_lookup('isnull')(Col(lhs, field, field), True)
                else:
                    lookup = field.get_lookup('exact')(Col(lhs, field, field), settings.FIELD_DEFAULT)

            cond.add(lookup, 'AND')
        return cond
    return wrapper


ForeignObject.get_extra_restriction = get_extra_restriction_patch(ForeignObject.get_extra_restriction)
