# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20150415_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabinvisitor',
            name='memberid_unrecognized',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
