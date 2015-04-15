# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20150415_1305'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinSettlement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.CharField(max_length=45)),
                ('transaction_id', models.CharField(max_length=100, null=True)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='cabinvisit',
            name='datetime',
        ),
        migrations.RemoveField(
            model_name='cabinvisit',
            name='order_number',
        ),
        migrations.RemoveField(
            model_name='cabinvisit',
            name='transaction_id',
        ),
        migrations.AddField(
            model_name='cabinvisit',
            name='cabin_object_id',
            field=models.CharField(default=None, max_length=24),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cabinvisit',
            name='cabin_settlement',
            field=models.ForeignKey(related_name='visits', default=None, to='user.CabinSettlement'),
            preserve_default=False,
        ),
    ]
