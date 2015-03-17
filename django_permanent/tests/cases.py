from django.db.models.signals import post_delete
from django.test import TestCase
from django.utils.timezone import now
from django.utils.unittest import skipUnless

from django_permanent.tests.cond import model_utils_installed

from .test_app.models import MyPermanentModel, RemovableDepended, NonRemovableDepended, PermanentDepended, CustomQsPermanent, MyPermanentModelWithManager


class TestDelete(TestCase):
    def setUp(self):
        self.permanent = MyPermanentModel.objects.create()

    def test_deletion(self):
        model = MyPermanentModel
        permanent2 = model.objects.create()
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [permanent2])
        self.assertEqual(list(model.all_objects.all()), [self.permanent, permanent2])
        self.assertEqual(list(model.deleted_objects.all()), [self.permanent])

    def test_depended(self):
        model = RemovableDepended
        model.objects.create(dependance=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [])

    def test_non_removable_depended(self):
        model = NonRemovableDepended
        depended = model.objects.create(dependance=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [depended])

    def test_permanent_depended(self):
        model = PermanentDepended
        depended = model.objects.create(dependance=self.permanent)
        self.permanent.delete()
        self.assertEqual(list(model.objects.all()), [])
        self.assertEqual(list(model.deleted_objects.all()), [depended])
        new_depended = model.all_objects.get(pk=depended.pk)
        new_permanent = MyPermanentModel.all_objects.get(pk=self.permanent.pk)
        self.assertTrue(new_depended.removed)
        self.assertTrue(new_permanent.removed)
        self.assertEqual(new_depended.dependance_id, self.permanent.id)

    def test_double_delete(self):
        self.called = 0
        def post_delete_receiver(*args, **kwargs):
            self.called += 1
        post_delete.connect(post_delete_receiver, sender=PermanentDepended)

        model = PermanentDepended
        model.objects.create(dependance=self.permanent, removed=now())
        model.objects.create(dependance=self.permanent)
        self.permanent.delete()
        self.assertEqual(self.called, 1)
        self.permanent.delete()


class TestIntegration(TestCase):
    def test_prefetch_bug(self):
        permanent1 = MyPermanentModel.objects.create()
        NonRemovableDepended.objects.create(dependance=permanent1)
        MyPermanentModel.objects.prefetch_related('nonremovabledepended_set').all()
        NonRemovableDepended.all_objects.prefetch_related('dependance').all()

    def test_related_manager_bug(self):
        permanent = MyPermanentModel.objects.create()
        PermanentDepended.objects.create(dependance=permanent)
        PermanentDepended.objects.create(dependance=permanent, removed=now())
        self.assertEqual(permanent.permanentdepended_set.count(), 1)


class TestPassThroughManager(TestCase):
    @skipUnless(model_utils_installed, "Missing django-model-utils")
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
