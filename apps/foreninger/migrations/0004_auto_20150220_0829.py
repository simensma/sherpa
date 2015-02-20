# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def add_object_ids(apps, schema_editor):
    def get_object_id(forening):
        NtbId = apps.get_model("sherpa2", "NtbId")
        try:
            return NtbId.objects.get(sql_id=forening.id, type='G').object_id
        except NtbId.DoesNotExist:
            return None

    Forening = apps.get_model("foreninger", "Forening")
    for forening in Forening.objects.all():
        forening.turbase_object_id = get_object_id(forening)
        forening.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foreninger', '0003_forening_turbase_object_id'),
    ]

    operations = [
        migrations.RunPython(add_object_ids)
    ]
