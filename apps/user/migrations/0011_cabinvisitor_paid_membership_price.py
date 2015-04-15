# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_cabinvisitor_memberid_unrecognized'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabinvisitor',
            name='paid_membership_price',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
