# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_cabin_visits(apps, schema_editor):
    CabinVisit = apps.get_model("user", "CabinVisit")
    CabinVisit.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20150226_1226'),
    ]

    operations = [
        migrations.RunPython(remove_cabin_visits)
    ]
