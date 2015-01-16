# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def remove_end_dates(apps, schema_editor):
    # Remove certificate end date for all ambassadører
    Turleder = apps.get_model("user", "Turleder")
    for turleder in Turleder.objects.filter(role='ambassadør'):
        turleder.date_end = None
        turleder.save()

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_end_dates),
    ]
