import django
from django.db.models.signals import post_delete
from django.test import TestCase
from django.utils.timezone import now
from django.utils.unittest import skipUnless

from django_permanent.tests.cond import model_utils

from .test_app.models import MyPermanentModel, RemovableDepended, NonRemovableDepended, PermanentDepended, \
    CustomQsPermanent, MyPermanentModelWithManager, M2MFrom, M2MTo, PermanentM2MThrough


class TestDelete(TestCase):
    def setUp(self):
        self.permanent = MyPermanentModel.objects.create()

    def test_deletion(self):
        model = MyPermanentModel
        permanent2 = model.objects.create()
        self.permanent.delete()
        self.assertTrue(self.permanent.removed)
        self.assertEqual(list(model.objects.all()), [permanent2])
        self.assertEqual(list(model.all_objects.all()), [self.permanent, permanent2])
        self.assertEqual(list(model.deleted_objects.all()), [self.permanent])

    def test_depended(self):
        model = RemovableDepended
        model.objects.create(dependence=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [])

    def test_non_removable_depended(self):
        model = NonRemovableDepended
        depended = model.objects.create(dependence=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [depended])

    def test_permanent_depended(self):
        model = PermanentDepended
        depended = model.objects.create(dependence=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [])
        self.assertEqual(list(model.deleted_objects.all()), [depended])
        new_depended = model.all_objects.get(pk=depended.pk)
        new_permanent = MyPermanentModel.all_objects.get(pk=self.permanent.pk)
        self.assertTrue(new_depended.removed)
        self.assertTrue(new_permanent.removed)
        self.assertEqual(new_depended.dependence_id, self.permanent.id)

    def test_double_delete(self):
        self.called = 0

        def post_delete_receiver(*args, **kwargs):
            self.called += 1

        post_delete.connect(post_delete_receiver, sender=PermanentDepended)

        model = PermanentDepended
        model.objects.create(dependence=self.permanent, removed=now())
        model.objects.create(dependence=self.permanent)
        self.permanent.delete()
        self.assertEqual(self.called, 1)

    def test_restore(self):
        self.permanent.delete()
        self.permanent.restore()
        self.assertFalse(self.permanent.removed)
        self.assertEqual(list(MyPermanentModel.objects.all()), [self.permanent])

    def test_forced_model_delete(self):
        self.permanent.delete(force=True)
        self.assertEqual(MyPermanentModel.all_objects.count(), 0)

    def test_forced_queryset_delete(self):
        MyPermanentModel.objects.all().delete(force=True)
        self.assertEqual(MyPermanentModel.all_objects.count(), 0)


class TestIntegration(TestCase):
    def test_prefetch_bug(self):
        permanent1 = MyPermanentModel.objects.create()
        NonRemovableDepended.objects.create(dependence=permanent1)
        MyPermanentModel.objects.prefetch_related('nonremovabledepended_set').all()
        NonRemovableDepended.all_objects.prefetch_related('dependence').all()

    def test_related_manager_bug(self):
        permanent = MyPermanentModel.objects.create()
        PermanentDepended.objects.create(dependence=permanent)
        PermanentDepended.objects.create(dependence=permanent, removed=now())
        self.assertEqual(permanent.permanentdepended_set.count(), 1)
        self.assertEqual(PermanentDepended.objects.count(), 1)

    def test_m2m_manager(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to, removed=now())
        self.assertEqual(_from.m2mto_set.count(), 0)

    def test_m2m_manager_clear(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to)
        self.assertEqual(_from.m2mto_set.count(), 1)
        _from.m2mto_set.clear()
        self.assertEqual(_from.m2mto_set.count(), 0)
        self.assertEqual(PermanentM2MThrough.objects.count(), 0)
        self.assertEqual(PermanentM2MThrough.all_objects.count(), 1)
        self.assertEqual(M2MFrom.objects.count(), 1)
        self.assertEqual(M2MTo.objects.count(), 1)

    def test_m2m_manager_delete(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to)
        self.assertEqual(_from.m2mto_set.count(), 1)
        _from.m2mto_set.all().delete()
        self.assertEqual(_from.m2mto_set.count(), 0)
        self.assertEqual(PermanentM2MThrough.objects.count(), 0)
        self.assertEqual(PermanentM2MThrough.all_objects.count(), 1)
        self.assertEqual(M2MFrom.objects.count(), 1)
        self.assertEqual(M2MTo.objects.count(), 0)

    def test_m2m_prefetch_related(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to)
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to, removed=now())
        self.assertSequenceEqual(M2MFrom.objects.prefetch_related('m2mto_set').get(pk=_from.pk).m2mto_set.all(), [_to])
        self.assertEqual(M2MFrom.objects.prefetch_related('m2mto_set').get(pk=_from.pk).m2mto_set.count(), 1)

    @skipUnless(django.VERSION < (1, 8, 0), "Missing django-model-utils")
    def test_m2m_select_related(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to)
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to, removed=now())
        self.assertSequenceEqual(M2MFrom.objects.select_related('m2mto_set').get(pk=_from.pk).m2mto_set.all(), [_to])
        self.assertEqual(M2MFrom.objects.select_related('m2mto_set').get(pk=_from.pk).m2mto_set.count(), 1)

    def test_m2m_all_objects(self):
        dependence = MyPermanentModel.objects.create(removed=now())
        depended = NonRemovableDepended.objects.create(dependence=dependence, removed=now())
        depended = NonRemovableDepended.all_objects.get(pk=depended.pk)
        self.assertEqual(depended.dependence, dependence)

    def test_m2m_deleted_through(self):
        _from = M2MFrom.objects.create()
        _to = M2MTo.objects.create()
        PermanentM2MThrough.objects.create(m2m_from=_from, m2m_to=_to, removed=now())
        self.assertEqual(M2MFrom.objects.filter(m2mto__id=_to.pk).count(), 0)


class TestPassThroughManager(TestCase):
    @skipUnless(model_utils, "Missing django-model-utils")
    def test_pass_through_manager(self):
        self.assertTrue(hasattr(CustomQsPermanent.objects, 'test'))
        self.assertTrue(hasattr(CustomQsPermanent.objects, 'restore'))
        self.assertTrue(CustomQsPermanent.objects.get_restore_or_create(id=10))


class TestCustomQSMethods(TestCase):
    def test__get_restore_or_create__get(self):
        self.obj = MyPermanentModel.objects.create(name="old")
        self.assertEqual(MyPermanentModel.objects.get_restore_or_create(name="old").id, 1)

    def test__get_restore_or_create__restore(self):
        obj = MyPermanentModel.objects.create(name="old", removed=now())
        self.assertEqual(MyPermanentModel.objects.get_restore_or_create(name="old").id, obj.id)
        self.assertEqual(MyPermanentModel.objects.count(), 1)
        self.assertEqual(MyPermanentModel.all_objects.count(), 1)

    def test__get_restore_or_create__create(self):
        MyPermanentModel.objects.get_restore_or_create(name="old")
        self.assertEqual(MyPermanentModel.objects.get_restore_or_create(name="old").id, 1)
        self.assertEqual(MyPermanentModel.objects.count(), 1)
        self.assertEqual(MyPermanentModel.all_objects.count(), 1)

    def test_restore(self):
        MyPermanentModel.objects.create(name="old", removed=now())
        MyPermanentModel.objects.filter(name="old").restore()
        self.assertEqual(MyPermanentModel.objects.count(), 1)
        self.assertEqual(MyPermanentModel.all_objects.count(), 1)

    def test_restore_on_create(self):
        MyPermanentModel.Permanent.restore_on_create = True
        first = MyPermanentModel.objects.create(name='unique', removed=now())
        second = MyPermanentModel.objects.create(name='unique')
        self.assertEqual(first, second)
        MyPermanentModel.Permanent.restore_on_create = False


class TestCustomManager(TestCase):
    def setUp(self):
        MyPermanentModelWithManager.objects.create(name="regular")
        MyPermanentModelWithManager.objects.create(name="removed", removed=now())

    def test_custom_method(self):
        MyPermanentModelWithManager.objects.test()

    def test_non_removed(self):
        self.assertEqual(MyPermanentModelWithManager.objects.count(), 1)

    def test_removed(self):
        self.assertEqual(MyPermanentModelWithManager.objects.count(), 1)

    def test_all(self):
        self.assertEqual(MyPermanentModelWithManager.any_objects.count(), 2)
