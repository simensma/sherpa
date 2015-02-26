# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_cabinvisit_cabinvisitor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabinvisit',
            name='transaction_id',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
