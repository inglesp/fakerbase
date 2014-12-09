from django.db import models


class _unicode__mixin(object):
    def __unicode__(self):
        attnames = [f.attname for f in self._meta.fields]
        return ', '.join('{}: {!r}'.format(a, getattr(self, a)) for a in attnames)


class M(models.Model, _unicode__mixin):
    a = models.IntegerField()
    b = models.IntegerField()
    c = models.CharField(max_length=255)


class N(models.Model, _unicode__mixin):
    a = models.IntegerField()
    m = models.ForeignKey('M')

