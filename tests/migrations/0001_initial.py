# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tests.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='M',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', models.IntegerField()),
                ('b', models.IntegerField()),
                ('c', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model, tests.models._unicode__mixin),
        ),
        migrations.CreateModel(
            name='N',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', models.IntegerField()),
                ('m', models.ForeignKey(to='tests.M')),
            ],
            options={
            },
            bases=(models.Model, tests.models._unicode__mixin),
        ),
        migrations.CreateModel(
            name='O',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', models.IntegerField()),
                ('n', models.ForeignKey(to='tests.N')),
            ],
            options={
            },
            bases=(models.Model, tests.models._unicode__mixin),
        ),
    ]
