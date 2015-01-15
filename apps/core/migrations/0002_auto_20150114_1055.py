# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='forening',
            field=models.ForeignKey(related_name=b'sites', to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='redirect',
            name='site',
            field=models.ForeignKey(related_name=b'redirects', to='core.Site'),
            preserve_default=True,
        ),
    ]
