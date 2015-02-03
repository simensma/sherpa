# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations

def add_gallery_layout_field(apps, schema_editor):
    Content = apps.get_model("page", "Content")
    for content in Content.objects.filter(type='widget'):
        content_json = json.loads(content.content)
        if content_json['widget'] == 'gallery':
            if 'layout' not in content_json:
                content_json['layout'] = 'carousel'
                content.content = json.dumps(content_json)
                content.save()

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0002_auto_20150128_1409'),
    ]

    operations = [
        migrations.RunPython(add_gallery_layout_field),
    ]
