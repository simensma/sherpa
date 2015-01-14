# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annonse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('date_renewed', models.DateField(auto_now_add=True)),
                ('title', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('image', models.CharField(max_length=2048)),
                ('image_thumb', models.CharField(max_length=2048)),
                ('text', models.TextField()),
                ('hidden', models.BooleanField(default=False)),
                ('hideage', models.BooleanField(default=False)),
                ('is_image_old', models.BooleanField(default=False)),
                ('county', models.ForeignKey(to='core.County', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
