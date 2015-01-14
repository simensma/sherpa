# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forening',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('focus_id', models.IntegerField(default=None, null=True)),
                ('type', models.CharField(max_length=255, choices=[('sentral', 'Sentral/nasjonal'), ('forening', 'Medlemsforening'), ('turlag', 'Lokalt turlag'), ('turgruppe', 'Turgruppe')])),
                ('group_type', models.CharField(default=b'', max_length=255, choices=[('barn', 'Barnas Turlag'), ('ung', 'Ungdom'), ('fjellsport', 'DNT Fjellsport'), ('senior', 'DNT Senior'), ('other', 'Andre turgrupper')])),
                ('post_address', models.CharField(default=b'', max_length=255)),
                ('visit_address', models.CharField(default=b'', max_length=255)),
                ('contact_person_name', models.CharField(default=b'', max_length=255)),
                ('phone', models.CharField(default=b'', max_length=255)),
                ('email', models.CharField(default=b'', max_length=255)),
                ('organization_no', models.CharField(default=b'', max_length=255)),
                ('gmap_url', models.CharField(default=b'', max_length=2048)),
                ('facebook_url', models.CharField(default=b'', max_length=2048)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
