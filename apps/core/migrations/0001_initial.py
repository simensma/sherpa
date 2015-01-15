# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=100)),
                ('area', models.FloatField(null=True)),
                ('perimeter', models.FloatField(null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FocusCountry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=255)),
                ('scandinavian', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=4)),
                ('name', models.CharField(max_length=255)),
                ('area', models.FloatField(null=True)),
                ('perimeter', models.FloatField(null=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('update_date', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(max_length=512)),
                ('destination', models.CharField(max_length=2048)),
            ],
            options={
                'ordering': ['path'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=255)),
                ('prefix', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255, choices=[(b'forening', 'Foreningens hjemmeside'), (b'hytte', 'Hjemmeside for en betjent hytte'), (b'kampanje', 'Kampanjeside'), (b'mal', 'Mal for nye nettsteder')])),
                ('template', models.CharField(max_length=255, choices=[(b'central', b'DNTs nasjonale nettsted'), (b'local', b'Medlemsforening eller turgruppe sitt nettsted')])),
                ('title', models.CharField(max_length=255)),
                ('analytics_ua', models.CharField(max_length=255, null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('template_main', models.BooleanField(default=False)),
                ('template_type', models.CharField(default=b'', max_length=255)),
                ('template_description', models.CharField(default=b'', max_length=1023)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zipcode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zipcode', models.CharField(max_length=4)),
                ('area', models.CharField(max_length=255)),
                ('city_code', models.CharField(max_length=4)),
                ('city', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZipcodeState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_update', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
