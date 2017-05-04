=========
CHANGELOG
=========


1.1.7 (development)
===================

- nothing changed yet


1.1.6 (2017-05-04)
==================

- Missing related model all_objects manager bug #65 (thanks @kregoslup)


1.1.5 (2017-03-02)
==================

+ readme code highlight (thanks @bashu)
- queryset values method bug #62 (thanks @tjacoel)


1.1.4 (2016-09-15)
==================

+ django 1.10 support #58 (thanks @atin65536)


1.1.3 (2016-09-08)
==================

+ django 1.9 support #56 (thanks @atin65536)
+ values_list support #56 (thanks @atin65536)
- QuerySet pickling bug #55 (thanks @atin65536)


1.1.2 (2016-03-30)
==================

- running setup.py without django bug #47


1.1.1 (2016-03-16)
==================

- ForeignKey on_delete behaviour bug (thanks @atin65536)


1.1.0 (2016-03-16)
==================

+ Django 1.9 support
+ QuerySetManager support
+ Python 3.5 support
* Fixed latest supported model_utls version
* Documentation fixes
- inf recursion on restore_on_create bug
- Python 2.6 support dropped

Thanks to @aidanlister, @atin65536 and @jarekwg, you are awesome!

1.0.12 (2015-11-27)
===================

- added pre_restore, post_restore signals thanks atin65536


1.0.11 (2015-05-29)
===================

- Fixed deepcopy()-ing PermanentQuerySet #30
- all_objects.select_related bug #31


1.0.10 (2015-04-03)
===================

- Skip test_m2m_select_related test on Django 1.8 #27
- Manager isn't available; PermanentModel is abstract #24
- Atomic only for django >= 1.8 #21
+ Django 1.8 support
+ ReverseSingleRelatedObjectDescriptor patch Bug #25
+ Do not try to restore deleted object if it is created already deleted #23


1.0.9 (2015-04-02)
==================

+ Transaction handling backward compatibility #21
* replaced create_many_related_manager patching with get_extra_restriction patch
- fixed removable m2m through #22


1.0.8 (2015-03-27)
==================

+ Returned force argument
+ Replace commit_on_success_unless_managed by atomic (thanks David Fischer)
+ Find packages recursively (thanks David Fischer)
+ Make setup.py executable (thanks David Fischer)


1.0.7 (2015-03-24)
==================

+ Setting trigger field for all removed objects
+ Trigger field model save now affects all objects


1.0.6 (2015-03-24)
==================

- Fixed PermanentModel.restore() fail
+ PermanentModel.delete() now sets removed attribute


1.0.5 (2015-03-23)
==================

- Removed fast_deletes fix
+ create_many_related_manager patch (For proper m2m)
+ Proper Collector patching
* proper Query patching/unpatching
+ restore_on_create feature


1.0.4 (2015-03-17)
==================

+ Many-to-many relations support
- get_restore_or_create bug
+ added MIDDLEWARE_CLASSES to reduce Django 1.7 output


1.0.3 (2015-03-17)
==================

+ Related manager tests
+ Double delete tests
- Disabled PermanentModels foreign key updates
+ _base_manager override
- Django 1.7 get_restore_or_create bug
+ Django 1.7 test structure support
- wrong version in master
+ include tests into the package
- Fixed get_restore_or_create hardcoded field name

1.0.2 (2014-02-05)
==================

- get_restore_or_create bug
+ Trigger field customisation support


1.0.1 (2014-02-03)
==================

- Prefetch related bug
* Django 1.6 transactions support
