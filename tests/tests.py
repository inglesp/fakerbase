from django.test import TestCase
from django.db.models import Q

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

    def test_exclude(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)

        self.assertItemsEqual([m2], M.objects.exclude(a=1))

    def test_filter_not(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)

        self.assertItemsEqual([m2], M.objects.filter(~Q(a=1)))

    def test_filter_and(self):
        m1 = M.objects.create(a=1, b=1)
        m2 = M.objects.create(a=1, b=2)
        m3 = M.objects.create(a=2, b=1)
        m4 = M.objects.create(a=2, b=2)

        self.assertItemsEqual([m3], M.objects.filter(a=2, b=1))
        self.assertItemsEqual([m3], M.objects.filter(a=2).filter(b=1))
        self.assertItemsEqual([m3], M.objects.filter(Q(a=2) & Q(b=1)))
        self.assertItemsEqual([m3], (M.objects.filter(a=2) & M.objects.filter(b=1)))

    def test_filter_or(self):
        m1 = M.objects.create(a=1, b=1)
        m2 = M.objects.create(a=1, b=2)
        m3 = M.objects.create(a=2, b=1)
        m4 = M.objects.create(a=2, b=2)

        self.assertItemsEqual([m1, m3, m4], (M.objects.filter(a=2) | M.objects.filter(b=1)))
        self.assertItemsEqual([m1, m3, m4], M.objects.filter(Q(a=2) | Q(b=1)))

    def test_filter_complex_boolean(self):
        m1 = M.objects.create(a=1, b=1)
        m2 = M.objects.create(a=1, b=2)
        m3 = M.objects.create(a=2, b=1)
        m4 = M.objects.create(a=2, b=2)

        self.assertItemsEqual([m1], M.objects.filter((Q(a=1) & ~Q(b=2)) & (Q(a=1) | ~Q(b=2))))

    def test_filter_lt(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        m3 = M.objects.create(a=3)

        self.assertItemsEqual([m1], M.objects.filter(a__lt=2))

    def test_filter_lte(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        m3 = M.objects.create(a=3)

        self.assertItemsEqual([m1, m2], M.objects.filter(a__lte=2))

    def test_filter_contains(self):
        m1 = M.objects.create(c='abc')
        m2 = M.objects.create(c='bcd')
        m3 = M.objects.create(c='cde')

        self.assertItemsEqual([m2, m3], M.objects.filter(c__contains='cd'))
