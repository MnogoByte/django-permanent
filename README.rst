Django Permanent
================

Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.

Models
================

To create non-deletable model just inherit it form the PermanentModel.::

    class MyModel(PermanentModel):
        pass

It automatically changes delete behaviour, to hide model instead of deleting. restore() method.::

    >>> a = MyModel.objects.create(pk=1)
    >>> b = MyModel.objects.create(pk=2)
    >>> MyModel.objects.count()
    2
    >>> a.delete()
    >>> MyModel.objects.count()
    1

To recover model just call its restore method.::

    >>> a.restore()
    >>> MyModel.objects.count()
    2

User Force kwarg to enforce physical deletion.::

    >>> a.delete(force=True) # Will act as the default django delete
    >>> MyModel._base_manager.count()
    0

Managers
================

It changes default model manager to ignore deleted objects. And adds deleted_objects manager to find the last ones.::

    >>> MyModel.objects.count()
    2
    >>> a.delete()
    >>> MyModel.objects.count()
    1
    >>> MyModel.deleted_objects.count()
    1
    >>> MyModel._defatult_manager.count()
    2

QuerySet
================
Query set delete method will act as the default django delete, with the one exception - all related  PermanentModel children will be marked as deleted, the usual models will be deleted physically::
        
    >>> MyModel.objects.all().delete()

You can still force django query set physical deletion::

    >>> MyModel.objects.all().delete(force=True)

model_utils.PassThroughManager compatibility 
================

1. Inherit your query set from PermanentQuerySet::

    class MyQuerySet(PermanentQuerySet)
        pass

2. Wrap it in the permanent_queryset or deleted_queryset in you model manager declaration::

    class MyModel(PermanentModel)
        objects = PassThroughManager.for_queryset_class(permanent_queryset(ServerFileQuerySet))()
        deleted_objects = PassThroughManager.for_queryset_class(deleted_queryset(ServerFileQuerySet))()

Field name
================

By default field is named removed, but you can override it by PERMANENT_FIELD variable in you settings.py.::

    PERMANENT_FIELD = 'deleted'
