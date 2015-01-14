# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foreninger', '0001_initial'),
        ('aktiviteter', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversionfailure',
            name='foreninger',
            field=models.ManyToManyField(related_name=b'failed_imports', null=True, to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitetimage',
            name='aktivitet',
            field=models.ForeignKey(related_name=b'images', to='aktiviteter.Aktivitet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitetdate',
            name='aktivitet',
            field=models.ForeignKey(related_name=b'dates', to='aktiviteter.Aktivitet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitetdate',
            name='participants',
            field=models.ManyToManyField(related_name=b'aktiviteter', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitetdate',
            name='turledere',
            field=models.ManyToManyField(related_name=b'turleder_aktivitet_dates', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='audiences',
            field=models.ManyToManyField(related_name=b'aktiviteter', to='aktiviteter.AktivitetAudience'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='category_tags',
            field=models.ManyToManyField(related_name=b'aktiviteter', to='core.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='co_foreninger',
            field=models.ManyToManyField(related_name=b'aktiviteter', null=True, to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='co_foreninger_cabin',
            field=models.ManyToManyField(related_name=b'+', null=True, to='aktiviteter.Cabin'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='counties',
            field=models.ManyToManyField(related_name=b'aktiviteter', to='core.County'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='forening',
            field=models.ForeignKey(related_name=b'+', to='foreninger.Forening', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='forening_cabin',
            field=models.ForeignKey(related_name=b'+', to='aktiviteter.Cabin', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aktivitet',
            name='municipalities',
            field=models.ManyToManyField(related_name=b'aktiviteter', to='core.Municipality'),
            preserve_default=True,
        ),
    ]
