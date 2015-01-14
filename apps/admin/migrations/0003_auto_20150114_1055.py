# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_release_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foreninger', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='forening',
            field=models.ForeignKey(to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='album',
            field=models.ForeignKey(related_name=b'images', to='admin.Album', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='tags',
            field=models.ManyToManyField(related_name=b'images', to='core.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='uploader',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fotokonkurranse',
            name='album',
            field=models.ForeignKey(to='admin.Album', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaigntext',
            name='campaign',
            field=models.ForeignKey(related_name=b'text', to='admin.Campaign'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='campaign',
            name='site',
            field=models.ForeignKey(to='core.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='album',
            name='parent',
            field=models.ForeignKey(to='admin.Album', null=True),
            preserve_default=True,
        ),
    ]
