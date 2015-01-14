# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foreninger', '0001_initial'),
        ('core', '0002_auto_20150114_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='forening',
            name='contact_person',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forening',
            name='counties',
            field=models.ManyToManyField(related_name=b'foreninger', to='core.County'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forening',
            name='parents',
            field=models.ManyToManyField(related_name=b'children', to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forening',
            name='zipcode',
            field=models.ForeignKey(to='core.Zipcode', null=True),
            preserve_default=True,
        ),
    ]
