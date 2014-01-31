from django.test import TestCase
from django.utils.unittest.case import skipUnless

from django_permanent.tests.cond import model_utils_installed

from .models import MyPermanentModel, RemovableDepended, NonRemovableDepended, PermanentDepended, CustomQsPermanent


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


class TestPassThroughManager(TestCase):
    @skipUnless(model_utils_installed, "Missing django-model-utils")
    def test_pass_through_manager(self):
        self.assertTrue(hasattr(CustomQsPermanent.objects, 'test'))
        self.assertTrue(hasattr(CustomQsPermanent.objects, 'restore'))
        self.assertTrue(CustomQsPermanent.objects.get_restore_or_create(id=10))
