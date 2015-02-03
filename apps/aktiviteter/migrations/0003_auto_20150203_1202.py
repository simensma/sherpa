# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aktiviteter', '0002_auto_20150114_1055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aktivitetdate',
            old_name='signup_max_allowed',
            new_name='max_participants',
        ),
    ]
