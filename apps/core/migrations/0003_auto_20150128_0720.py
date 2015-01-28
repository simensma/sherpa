# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models, migrations

def update_domain(apps, schema_editor):
    Site = apps.get_model("core", "Site")
    for site in Site.objects.filter(domain__endswith='turistforeningen.no'):
        site.domain = re.sub("turistforeningen.no", "dnt.no", site.domain)
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150114_1055'),
    ]

    operations = [
        migrations.RunPython(update_domain),
    ]
