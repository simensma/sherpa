# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0006_auto_20150220_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='lodging',
            name='forening',
            field=models.ForeignKey(default=46, to='foreninger.Forening'),
            preserve_default=False,
        ),
    ]
