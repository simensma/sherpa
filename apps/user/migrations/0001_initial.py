# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('identifier', models.CharField(unique=True, max_length=255, db_index=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=75)),
                ('sherpa_email', models.EmailField(max_length=75)),
                ('memberid', models.IntegerField(unique=True, null=True)),
                ('is_inactive', models.BooleanField(default=False)),
                ('is_expired', models.BooleanField(default=False)),
                ('is_pending', models.BooleanField(default=False)),
                ('pending_registration_key', models.CharField(max_length=40, null=True)),
                ('password_restore_key', models.CharField(max_length=40, null=True)),
                ('password_restore_date', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForeningRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255, choices=[(b'admin', b'Administrator'), (b'user', b'Vanlig bruker')])),
                ('forening', models.ForeignKey(to='foreninger.Forening')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instruktor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255)),
                ('user', models.ForeignKey(related_name=b'instruktor', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Kursleder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_start', models.DateField(null=True)),
                ('date_end', models.DateField(null=True)),
                ('user', models.OneToOneField(related_name=b'kursleder', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NorwayBusTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_placed', models.DateTimeField(auto_now_add=True)),
                ('date_trip', models.DateTimeField(null=True)),
                ('date_trip_text', models.CharField(max_length=25)),
                ('distance', models.CharField(max_length=1024)),
                ('is_imported', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name=b'norway_bus_ticket', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Turleder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255, choices=[('vinter', 'Vinterturleder'), ('sommer', 'Sommerturleder'), ('grunnleggende', 'Grunnleggende turleder'), ('ambassad\xf8r', 'DNT Ambassad\xf8r')])),
                ('date_start', models.DateField(null=True)),
                ('date_end', models.DateField(null=True)),
                ('forening_approved', models.ForeignKey(related_name=b'turledere_approved', to='foreninger.Forening')),
                ('user', models.ForeignKey(related_name=b'turledere', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='foreninger',
            field=models.ManyToManyField(related_name=b'+', through='user.ForeningRole', to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='permissions',
            field=models.ManyToManyField(related_name=b'+', to='user.Permission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='turleder_active_foreninger',
            field=models.ManyToManyField(related_name=b'active_turledere', to='foreninger.Forening'),
            preserve_default=True,
        ),
    ]
