# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20150226_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cabinvisitor',
            name='cabin_visit',
            field=models.ForeignKey(related_name='visitors', to='user.CabinVisit'),
            preserve_default=True,
        ),
    ]
