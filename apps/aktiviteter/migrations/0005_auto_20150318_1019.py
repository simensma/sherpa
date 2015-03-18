# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate(apps, schema_editor):
    AktivitetDate = apps.get_model("aktiviteter", "AktivitetDate")
    for d in AktivitetDate.objects.filter(signup_simple_allowed=True):
        d.signup_simple_allowed = False
        d.save()

class Migration(migrations.Migration):

    dependencies = [
        ('aktiviteter', '0004_aktivitet_sherpa2_signup'),
    ]

    operations = [
        migrations.RunPython(migrate),
    ]
