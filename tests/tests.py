from django.test import TestCase
from django.db.models import F, Q

from .models import M, N, O, P

try:
    TestCase.assertItemsEqual
except AttributeError:
    # python3
    TestCase.assertItemsEqual = TestCase.assertCountEqual


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

    def test_filter_references(self):
        m1 = M.objects.create(a=1, b=2)
        m2 = M.objects.create(a=2, b=1)

        self.assertItemsEqual([m2], M.objects.filter(a__gt=F('b')))


class RelationshipTests(TestCase):
    def test_foreign_key(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        n1 = N.objects.create(m=m1)
        n2 = N.objects.create(m=m1)
        n3 = N.objects.create(m=m2)

        self.assertItemsEqual([n1, n2], N.objects.filter(m__a=1))

    def test_foreign_key_reverse(self):
        m1 = M.objects.create()
        m2 = M.objects.create()
        n1 = N.objects.create(a=1, m=m1)
        n2 = N.objects.create(a=2, m=m1)
        n3 = N.objects.create(a=3, m=m2)

        self.assertItemsEqual([m1], M.objects.filter(n__a=1))

    def test_foreign_key_through(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        n1 = N.objects.create(m=m1)
        n2 = N.objects.create(m=m1)
        n3 = N.objects.create(m=m2)
        o1 = O.objects.create(n=n1)
        o2 = O.objects.create(n=n2)
        o3 = O.objects.create(n=n3)

        self.assertItemsEqual([o1, o2], O.objects.filter(n__m__a=1))

    def test_foreign_key_reverse_through(self):
        m1 = M.objects.create()
        m2 = M.objects.create()
        n1 = N.objects.create(m=m1)
        n2 = N.objects.create(m=m1)
        n3 = N.objects.create(m=m2)
        o1 = O.objects.create(a=1, n=n1)
        o2 = O.objects.create(a=1, n=n2)
        o3 = O.objects.create(a=2, n=n3)

        self.assertItemsEqual([m1], M.objects.filter(n__o__a=1))

    def test_many_to_many(self):
        m1 = M.objects.create(a=1)
        m2 = M.objects.create(a=2)
        p1 = P.objects.create()
        p2 = P.objects.create()
        p3 = P.objects.create()
        p1.ms.add(m1)
        p2.ms.add(m1)
        p3.ms.add(m2)

        self.assertItemsEqual([p1, p2], P.objects.filter(ms__a=1))

    def test_many_to_many_reverse(self):
        m1 = M.objects.create()
        m2 = M.objects.create()
        p1 = P.objects.create(a=1)
        p2 = P.objects.create(a=2)
        p3 = P.objects.create(a=3)
        p1.ms.add(m1)
        p2.ms.add(m1)
        p3.ms.add(m2)

        self.assertItemsEqual([m1], M.objects.filter(p__a=1))
