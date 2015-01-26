# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import migrations

def update_domain(apps, schema_editor):
    Menu = apps.get_model("page", "Menu")
    for menu in Menu.objects.all():
        menu.url = re.sub("www.turistforeningen.no", "www.dnt.no", menu.url)
        menu.save()

    Content = apps.get_model("page", "Content")
    for content in Content.objects.all():
        content.content = re.sub("www.turistforeningen.no", "www.dnt.no", content.content)
        content.save()

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_domain),
    ]
