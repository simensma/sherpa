# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aktiviteter', '0006_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='participantgroup',
            name='comment',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
