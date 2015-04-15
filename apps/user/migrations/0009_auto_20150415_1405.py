# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_cabinsettlement_payer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cabinsettlement',
            old_name='payer',
            new_name='paying_user',
        ),
    ]
