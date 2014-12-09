from django.test import TestCase
from django.db.models import Q

from .models import M, N


class AllTests(TestCase):
    def test_all(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)

        self.assertItemsEqual([m1, m2], M.objects.all())


class FilterTests(TestCase):
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


class RelationshipTests(TestCase):
    def test_many_to_one(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        n1 = N.objects.create(m=m1)
        n2 = N.objects.create(m=m1)
        n3 = N.objects.create(m=m2)

        self.assertItemsEqual([n1, n2], N.objects.filter(m__a=1))

    def test_one_to_many(self):
        m1 = M.objects.create()
        m2 = M.objects.create()
        n1 = N.objects.create(a=1, m=m1)
        n2 = N.objects.create(a=2, m=m1)
        n3 = N.objects.create(a=3, m=m2)

        self.assertItemsEqual([m1], M.objects.filter(n__a=1))
