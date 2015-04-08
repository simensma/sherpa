# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def reset_tree_ids(apps, schema_editor):
    Site = apps.get_model("core", "Site")
    Page = apps.get_model("page", "Page")

    # It doesn't matter what the tree ID is, as long as it's unique for each tree
    # See http://django-mptt.github.io/django-mptt/technical_details.html
    for tree_id, site in enumerate(Site.objects.all(), 1):
        Page.objects.filter(site=site).update(tree_id=tree_id)

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0005_auto_20150326_2010'),
    ]

    operations = [
        migrations.RunPython(reset_tree_ids),
    ]
