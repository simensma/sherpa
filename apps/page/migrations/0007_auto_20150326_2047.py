# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def rebuild(apps, schema_editor):
    # We don't really care about the state of the database, as long as it's still there and using MPTT.
    # If that's not the case, and you try to apply migrations in the faaaar future, this may come back to haunt you.
    # In that case you don't care about the state of the data so just comment this entire method out and replace it
    # with 'pass'. PROBLEM SOLVED! http://i.imgur.com/4mYD13u.gif
    from page.models import Page # YES, intentional model import; not using the migration ORM layer
    Page.objects.rebuild()

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0006_auto_20150326_2022'),
    ]

    operations = [
        migrations.RunPython(rebuild),
    ]
