# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def fix_parents(apps, schema_editor):
    Site = apps.get_model("core", "Site")
    Page = apps.get_model("page", "Page")

    for p in Page.objects.filter(parent__isnull=False).order_by('level'):
        if p.site == p.parent.site:
            continue

        try:
            new_parent = Page.objects.get(title=p.parent.title, site=p.site)
            p.parent = new_parent
            p.save()
        except:
            # Handled these manually
            if p.parent.title == u'Våre hytter':
                new_parent = Page.objects.get(title=u'Forside', site=p.site)
                p.parent = new_parent
                p.save()
            elif p.parent.title == u'Om oss':
                new_parent = Page.objects.get(title=u'Om TTF', site=p.site)
                p.parent = new_parent
                p.save()
            else:
                raise Exception("Unexpected page not handled manually: %s" % p.id)

class Migration(migrations.Migration):

    dependencies = [
        ('page', '0004_merge'),
    ]

    operations = [
        migrations.RunPython(fix_parents),
    ]
