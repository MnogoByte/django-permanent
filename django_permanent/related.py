from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor as Descriptor,
)

from . import settings


def get_queryset_patch(func):
    def wrapper(self, **hints):
        from .models import PermanentModel

        instance = hints.get("instance")
        if (
            instance
            and isinstance(instance, PermanentModel)
            and getattr(instance, settings.FIELD)
        ):
            model = self.field.remote_field.model
            if hasattr(model, "all_objects"):
                return model.all_objects
            return model.objects
        return func(self, **hints)

    return wrapper


Descriptor.get_queryset = get_queryset_patch(Descriptor.get_queryset)
