from django.db import models


class M(models.Model):
    a = models.IntegerField()
    b = models.IntegerField()
    c = models.CharField(max_length=255)

    def __unicode__(self):
        attnames = [f.attname for f in self._meta.fields]
        return ', '.join('{}: {!r}'.format(a, getattr(self, a)) for a in attnames)
