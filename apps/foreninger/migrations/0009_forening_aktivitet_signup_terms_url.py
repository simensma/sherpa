# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0008_auto_20150220_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='forening',
            name='aktivitet_signup_terms_url',
            field=models.CharField(default='', max_length=2048),
            preserve_default=False,
        ),
    ]
