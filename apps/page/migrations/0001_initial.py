# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0002_auto_20150114_1055'),
        ('analytics', '0002_auto_20150114_1055'),
        ('core', '0002_auto_20150114_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('extension', models.CharField(max_length=4)),
                ('destination', models.CharField(max_length=2048)),
                ('sha1_hash', models.CharField(max_length=40)),
                ('content_script', models.CharField(default=b'', max_length=1023)),
                ('content_type', models.CharField(max_length=200)),
                ('width', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('viewcounter', models.CharField(max_length=2048)),
                ('fallback_extension', models.CharField(max_length=4, null=True)),
                ('fallback_sha1_hash', models.CharField(max_length=40, null=True)),
                ('fallback_content_type', models.CharField(max_length=200, null=True)),
                ('site', models.ForeignKey(to='core.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AdPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('view_limit', models.IntegerField(null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('views', models.IntegerField(default=0)),
                ('clicks', models.IntegerField(default=0)),
                ('ad', models.ForeignKey(to='page.Ad')),
                ('site', models.ForeignKey(to='core.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('span', models.IntegerField()),
                ('offset', models.IntegerField()),
                ('order', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('type', models.CharField(max_length=255, choices=[(b'widget', b'Widget'), (b'html', b'HTML'), (b'image', b'Image'), (b'title', b'Title')])),
                ('order', models.IntegerField()),
                ('column', models.ForeignKey(related_name=b'contents', to='page.Column')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=2048)),
                ('order', models.IntegerField()),
                ('site', models.ForeignKey(to='core.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('published', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(null=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('created_by', models.ForeignKey(related_name=b'pages_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name=b'pages_modified', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', mptt.fields.TreeForeignKey(to='page.Page', null=True)),
                ('site', models.ForeignKey(to='core.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('priority', models.IntegerField()),
                ('article', models.ForeignKey(to='articles.Article', null=True)),
                ('owner', models.ForeignKey(related_name=b'+', to=settings.AUTH_USER_MODEL)),
                ('page', models.ForeignKey(to='page.Page', null=True)),
                ('segment', models.ForeignKey(to='analytics.Segment', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('ads', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(related_name=b'+', to=settings.AUTH_USER_MODEL)),
                ('publishers', models.ManyToManyField(related_name=b'versions', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(related_name=b'versions', to='core.Tag')),
                ('variant', models.ForeignKey(to='page.Variant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='row',
            name='version',
            field=models.ForeignKey(related_name=b'rows', to='page.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='column',
            name='row',
            field=models.ForeignKey(related_name=b'columns', to='page.Row'),
            preserve_default=True,
        ),
    ]
