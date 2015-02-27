# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aktiviteter', '0003_auto_20150203_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='aktivitet',
            name='sherpa2_signup',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
