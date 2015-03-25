# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import boto

from core.util import s3_bucket

def fix_content_types(apps, schema_editor):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    for key in bucket.list(prefix='files/'):
        if key.name.endswith('/'):
            continue

        key = bucket.get_key(key.name) # Retrieve the key specifically since list() doesn't return any metadata
        print(key)
        content_type = key.content_type.replace('%2F', '/').encode('utf-8')
        key = key.copy(key.bucket.name, key.name, metadata={'Content-Type': content_type}, preserve_acl=True)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150128_0720'),
    ]

    operations = [
        migrations.RunPython(fix_content_types),
    ]
