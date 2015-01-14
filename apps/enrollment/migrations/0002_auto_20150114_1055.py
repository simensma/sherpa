# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foreninger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pending_user',
            field=models.ForeignKey(related_name=b'enrollment_users', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='enrollment',
            field=models.ForeignKey(related_name=b'transactions', to='enrollment.Enrollment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enrollment',
            name='forening',
            field=models.ForeignKey(related_name=b'+', to='foreninger.Forening', null=True),
            preserve_default=True,
        ),
    ]
