# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='tags',
            field=models.ManyToManyField(related_name=b'releases', to='core.Tag'),
            preserve_default=True,
        ),
    ]
