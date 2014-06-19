# -*- coding: utf-8 -*-
from operator import attrgetter

from django.db import transaction
from django.db.models.deletion import Collector as BaseCollector
from django.db.models import signals, sql
from django.utils import six
from django.utils.timezone import now

from . import PERMANENT_FIELD


class PermanentCollector(BaseCollector):
    fast_deletes = []

    def delete(self):
        """
            Patched the BaseCollector.delete with soft delete support for PermanentModel
        """
        from .models import PermanentModel
        time = now()

        # sort instance collections
        for model, instances in self.data.items():
            self.data[model] = sorted(instances, key=attrgetter("pk"))

        # if possible, bring the models in an order suitable for databases that
        # don't support transactions or cannot defer constraint checks until the
        # end of a transaction.
        self.sort()

        with transaction.commit_on_success_unless_managed(using=self.using):
            # send pre_delete signals
            for model, obj in self.instances_with_model():
                if not model._meta.auto_created:
                    signals.pre_delete.send(
                        sender=model, instance=obj, using=self.using
                    )

            # fast deletes
            for qs in self.fast_deletes:
                if issubclass(qs.model, PermanentModel):  # Update PermanentModel instance
                    pk_list = [obj.pk for obj in qs]
                    qs = sql.UpdateQuery(qs.model)
                    qs.update_batch(pk_list, {PERMANENT_FIELD: time}, self.using)
                else:
                    qs._raw_delete(using=self.using)

            # update fields
            for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
                query = sql.UpdateQuery(model)
                for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                    query.update_batch([obj.pk for obj in instances],
                                       {field.name: value}, self.using)

            # reverse instance collections
            for instances in six.itervalues(self.data):
                instances.reverse()

            # delete instances
            for model, instances in six.iteritems(self.data):
                pk_list = [obj.pk for obj in instances]
                if issubclass(model, PermanentModel):
                    query = sql.UpdateQuery(model)
                    query.update_batch(pk_list, {PERMANENT_FIELD: time}, self.using)
                else:
                    query = sql.DeleteQuery(model)
                    query.delete_batch(pk_list, self.using)

                if not model._meta.auto_created:
                    for obj in instances:
                        signals.post_delete.send(
                            sender=model, instance=obj, using=self.using
                        )

        # update collected instances
        for model, instances_for_fieldvalues in six.iteritems(self.field_updates):
            for (field, value), instances in six.iteritems(instances_for_fieldvalues):
                for obj in instances:
                    setattr(obj, field.attname, value)
        for model, instances in six.iteritems(self.data):
            for instance in instances:
                if issubclass(model, PermanentModel):
                    continue
                setattr(instance, model._meta.pk.attname, None)
