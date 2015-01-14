# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aktivitet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_point', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True)),
                ('omrader', djorm_pgarray.fields.TextArrayField(default=[], dbtype='text')),
                ('getting_there', models.TextField()),
                ('turforslag', models.IntegerField(null=True)),
                ('difficulty', models.CharField(max_length=255, choices=[(b'easy', b'Enkel'), (b'medium', b'Middels'), (b'hard', b'Krevende'), (b'expert', b'Ekspert')])),
                ('category', models.CharField(max_length=255, choices=[(b'organizedhike', b'Fellestur'), (b'course', b'Kurs'), (b'event', b'Arrangement'), (b'volunteerwork', b'Dugnad')])),
                ('category_type', models.CharField(default=b'', max_length=255)),
                ('pub_date', models.DateField()),
                ('published', models.BooleanField(default=False)),
                ('private', models.BooleanField(default=False)),
                ('sherpa2_id', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AktivitetAudience',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, choices=[(b'adults', b'Voksne'), (b'children', b'Barn'), (b'youth', b'Ungdom'), (b'senior', b'Seniorer'), (b'mountaineers', b'Fjellsportinteresserte'), (b'disabled', b'Funksjonshemmede')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AktivitetDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField(db_index=True)),
                ('end_date', models.DateTimeField()),
                ('signup_enabled', models.BooleanField(default=True)),
                ('signup_montis', models.BooleanField(default=False)),
                ('signup_simple_allowed', models.BooleanField(default=False)),
                ('signup_max_allowed', models.PositiveIntegerField(default=0, null=True)),
                ('signup_start', models.DateField(null=True)),
                ('signup_deadline', models.DateField(null=True)),
                ('cancel_deadline', models.DateField(null=True)),
                ('should_have_turleder', models.BooleanField(default=False)),
                ('meeting_place', models.TextField()),
                ('meeting_time', models.DateTimeField(null=True)),
                ('contact_type', models.CharField(default='arrang\xf8r', max_length=255, choices=[('arrang\xf8r', b'Arrang\xc3\xb8rforening'), ('turleder', b'Turleder'), ('custom', b'Skriv inn')])),
                ('contact_custom_name', models.CharField(max_length=255)),
                ('contact_custom_phone', models.CharField(max_length=255)),
                ('contact_custom_email', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AktivitetImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=2048)),
                ('text', models.CharField(max_length=1024)),
                ('photographer', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('sherpa2_url', models.CharField(max_length=1023, null=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cabin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('sherpa2_id', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConversionFailure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sherpa2_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('latest_date', models.DateField(null=True)),
                ('reason', models.CharField(max_length=255, choices=[(b'owner_doesnotexist', b'Aktiviteten er koblet til en arrang\xc3\xb8r som ikke finnes i nye Sherpa'), (b'no_owners', b'Aktiviteten har ingen arrang\xc3\xb8r.'), (b'date_without_start_date', b'Aktiviteten har en avgang uten noen startdato.'), (b'date_with_invalid_start_date', b'Aktiviteten har en avgang med ugyldig startdato.'), (b'date_without_end_date', b'Aktiviteten har en avgang uten noen sluttdato.'), (b'date_with_invalid_end_date', b'Aktiviteten har en avgang med ugyldig sluttdato.')])),
                ('cabins', models.ManyToManyField(related_name=b'failed_imports', null=True, to='aktiviteter.Cabin')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimpleParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('aktivitet_date', models.ForeignKey(related_name=b'simple_participants', to='aktiviteter.AktivitetDate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SynchronizationDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
