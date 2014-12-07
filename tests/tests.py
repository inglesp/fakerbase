from django.test import TestCase

from .models import M


class AllTest(TestCase):
    def test_filter(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)

        self.assertItemsEqual([m1, m2], M.objects.all())


class FilterTest(TestCase):
    def test_filter(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)

        self.assertItemsEqual([m1], M.objects.filter(a=1))

