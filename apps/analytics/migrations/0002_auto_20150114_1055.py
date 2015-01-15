# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='site',
            field=models.ForeignKey(to='core.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notfound',
            name='site',
            field=models.ForeignKey(to='core.Site'),
            preserve_default=True,
        ),
    ]
