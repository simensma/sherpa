# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0007_lodging_forening'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lodging',
            name='forening',
            field=models.ForeignKey(related_name='lodging_prices', to='foreninger.Forening'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='supply',
            name='supply_category',
            field=models.ForeignKey(related_name='supplies', to='foreninger.SupplyCategory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='supplycategory',
            name='forening',
            field=models.ForeignKey(related_name='supply_categories', to='foreninger.Forening'),
            preserve_default=True,
        ),
    ]
