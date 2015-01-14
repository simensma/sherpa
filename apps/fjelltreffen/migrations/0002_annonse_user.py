# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fjelltreffen', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='annonse',
            name='user',
            field=models.ForeignKey(related_name=b'fjelltreffen_annonser', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
