# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aktiviteter', '0004_aktivitet_sherpa2_signup'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aktivitet_date', models.ForeignKey(related_name='participant_groups', to='aktiviteter.AktivitetDate')),
                ('participants', models.ManyToManyField(related_name='aktivitet_groups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
