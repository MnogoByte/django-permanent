# -*- coding: utf-8 -*-
from operator import attrgetter

from django.db.models.deletion import Collector as BaseCollector, force_managed
from django.db.models import signals, sql
from django.utils import six
from django.utils.timezone import now

from . import PERMANENT_FIELD


class PermanentCollector(BaseCollector):

    @force_managed
    def delete(self):
        """
            Copy of the BaseCollector.delete with soft delete support for PermanentModel
        """
        from .models import PermanentModel

        time = now()

        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        self.sort()

        for model, obj in self.instances_with_model():
            if not model._meta.auto_created:
                signals.pre_delete.send(
                    sender=model, instance=obj, using=self.using
                )

        for qs in self.fast_deletes:
            if issubclass(qs.model, PermanentModel):  # Update PermanentModel instance
                qs.using(self.using).update(**{PERMANENT_FIELD: time})
            else:
                qs._raw_delete(using=self.using)

        for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
            query = sql.UpdateQuery(model)
            for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                if issubclass(model, PermanentModel):
                    query.update_batch([obj.pk for obj in instances],
                                       {field.name: value}, self.using)

        for instances in six.itervalues(self.data):
            instances.reverse()

        for model, batches in six.iteritems(self.batches):
            if issubclass(model, PermanentModel):  # Update PermanentModel instance
                query = sql.UpdateQuery(model)
                for field, instances in six.iteritems(batches):
                    query.update_batch([obj.pk for obj in instances], {PERMANENT_FIELD: time}, self.using)
            else:
                query = sql.DeleteQuery(model)
                for field, instances in six.iteritems(batches):
                    query.delete_batch([obj.pk for obj in instances], self.using, field)

        for model, instances in six.iteritems(self.data):
            pk_list = [obj.pk for obj in instances]
            if issubclass(model, PermanentModel):  # Update PermanentModel instance
                query = sql.UpdateQuery(model)
                query.update_batch(pk_list, {PERMANENT_FIELD: time}, self.using)
            else:
                query = sql.DeleteQuery(model)
                query.delete_batch(pk_list, self.using)

        for model, obj in self.instances_with_model():
            if not model._meta.auto_created:
                signals.post_delete.send(
                    sender=model, instance=obj, using=self.using
                )

        for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
            for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in six.iteritems(self.data):
            for instance in instances:
                setattr(instance, model._meta.pk.attname, None)
