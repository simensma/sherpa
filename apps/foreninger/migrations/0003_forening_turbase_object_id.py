# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0002_auto_20150114_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='forening',
            name='turbase_object_id',
            field=models.CharField(max_length=24, null=True),
            preserve_default=True,
        ),
    ]
