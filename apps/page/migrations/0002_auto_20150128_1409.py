# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations

def rename_widget(apps, schema_editor):
    Content = apps.get_model("page", "Content")
    for content in Content.objects.filter(type='widget'):
        content_json = json.loads(content.content)
        if content_json['widget'] == 'carousel':
            content_json['widget'] = 'gallery'
        content.content = json.dumps(content_json)
        content.save()

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_widget),
    ]
