Django Permanent
================

Yet another approach to provide soft (logical) delete or masking (thrashing) django models instead of deleting them physically from db.

.. image:: https://api.travis-ci.org/MnogoByte/django-permanent.svg?branch=master

Models
================

To create a non-deletable model just inherit it from ``PermanentModel``:

.. code-block:: python

    class MyModel(PermanentModel):
        pass

It automatically changes delete behaviour to hide objects instead of deleting them:

.. code-block:: python

    >>> a = MyModel.objects.create(pk=1)
    >>> b = MyModel.objects.create(pk=2)
    >>> MyModel.objects.count()
    2
    >>> a.delete()
    >>> MyModel.objects.count()
    1

To recover a deleted object just call its ``restore`` method:

.. code-block:: python

    >>> a.restore()
    >>> MyModel.objects.count()
    2

Use the ``force`` kwarg to enforce physical deletion:

.. code-block:: python

    >>> a.delete(force=True) # Will act as the default django delete
    >>> MyModel._base_manager.count()
    0

If you need to restore a deleted object instead of re-creating the same one use the ``restore_on_create`` attribute:

.. code-block:: python

    class MyModel(PermanentModel):
        class Permanent:
          restore_on_create = True

In this case ``QuerySet`` provides check existence of same attribute objects and restores them if they've been deleted, creating new ones if not.

Managers
========

It changes the default model manager to ignore deleted objects, adding a ``deleted_objects`` manager to see them instead:

.. code-block:: python

    >>> MyModel.objects.count()
    2
    >>> a.delete()
    >>> MyModel.objects.count()
    1
    >>> MyModel.deleted_objects.count()
    1
    >>> MyModel.all_objects.count()
    2
    >>> MyModel._base_manager.count()
    2

QuerySet
========

The ``QuerySet.delete`` method will act as the default django delete, with one exception - objects of models subclassing ``PermanentModel`` will be marked as deleted; the rest will be deleted physically:

.. code-block:: python

    >>> MyModel.objects.all().delete()

You can still force django query set physical deletion:

.. code-block:: python

    >>> MyModel.objects.all().delete(force=True)

Using custom querysets
======================

1. Inherit your query set from ``PermanentQuerySet``:

   .. code-block:: python

        class ServerFileQuerySet(PermanentQuerySet)
            pass

2. Wrap ``PermanentQuerySet`` or ``DeletedQuerySet`` in you model manager declaration:

   .. code-block:: python

        class MyModel(PermanentModel)
            objects = MultiPassThroughManager(ServerFileQuerySet, NonDeletedQuerySet)
            deleted_objects = MultiPassThroughManager(ServerFileQuerySet, DeletedQuerySet)
            all_objects = MultiPassThroughManager(ServerFileQuerySet, PermanentQuerySet)

Method ``get_restore_or_create``
================================

1. Check for existence of the object.
2. Restore it if it was deleted.
3. Create a new one, if it was never created.

Field name
==========

The default field named is 'removed', but you can override it with the PERMANENT_FIELD variable in settings.py:

.. code-block:: python

    PERMANENT_FIELD = 'deleted'

Requirements
============

- Django 1.7+
- Python 2.7, 3.4+
