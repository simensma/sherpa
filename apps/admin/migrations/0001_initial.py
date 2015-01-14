# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('ga_event_label', models.CharField(max_length=255)),
                ('utm_campaign', models.CharField(max_length=255)),
                ('image_original', models.CharField(max_length=2048)),
                ('image_cropped_hash', models.CharField(max_length=255)),
                ('image_crop', models.CharField(max_length=1024)),
                ('photographer', models.CharField(max_length=255)),
                ('photographer_alignment', models.CharField(max_length=10, choices=[('left', 'Venstre'), ('right', 'H\xf8yre')])),
                ('photographer_color', models.CharField(max_length=10, choices=[('white', 'Hvit'), ('black', 'Sort')])),
                ('button_enabled', models.BooleanField(default=True)),
                ('button_label', models.CharField(max_length=1024)),
                ('button_anchor', models.CharField(max_length=2048)),
                ('button_large', models.BooleanField(default=False)),
                ('button_position', models.CharField(max_length=512)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CampaignText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=1024)),
                ('style', models.CharField(max_length=1024)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fotokonkurranse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=8)),
                ('extension', models.CharField(max_length=4)),
                ('hash', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('photographer', models.CharField(max_length=255)),
                ('credits', models.CharField(max_length=255)),
                ('licence', models.CharField(max_length=1023)),
                ('exif', models.TextField()),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('access', models.CharField(default=b'all', max_length=255, choices=[(b'all', b'Alle medlemmer'), (b'forening', b'Medlemmer i foreningen eller underforeninger')])),
                ('license', models.CharField(default=b'all_rights_reserved', max_length=255, choices=[(b'all_rights_reserved', b'Alle rettigheter reservert'), (b'cc-by-nc-nd', b'Creative Commons Navngivelse-Ikkekommersiell-IngenBearbeidelse 3.0')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('cover_photo', models.CharField(max_length=2048)),
                ('description', models.TextField()),
                ('pdf_hash', models.CharField(max_length=40)),
                ('pdf_file_size', models.IntegerField(default=None, null=True)),
                ('online_view', models.CharField(max_length=2048)),
                ('pub_date', models.DateTimeField()),
                ('publication', models.ForeignKey(related_name=b'releases', to='admin.Publication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
