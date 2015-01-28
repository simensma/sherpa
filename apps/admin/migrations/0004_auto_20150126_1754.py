# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import migrations

def update_domain(apps, schema_editor):
    Campaign = apps.get_model("admin", "Campaign")
    for campaign in Campaign.objects.all():
        campaign.button_anchor = re.sub("www.turistforeningen.no", "www.dnt.no", campaign.button_anchor)
        campaign.save()

class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_auto_20150114_1055'),
    ]

    operations = [
        migrations.RunPython(update_domain),
    ]
