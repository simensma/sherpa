# encoding: utf-8
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import boto

from admin.models import Image
from page.models import Content
from core.util import s3_bucket

class Command(BaseCommand):
    args = u""
    help = u"Fjerner bilder i bildearkiv-mappa på S3 som ikke er referert i databasen lengre"

    def handle(self, *args, **options):
        if raw_input("Du bør kun kjøre dette scriptet på produksjonsserveren.\nSkriv 'prod' for vise at du vet hva du gjør: ") != 'prod':
            self.stdout.write("Avbryter.\n")
            return

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        buck = conn.get_bucket(s3_bucket())

        ghost_keys = []

        self.stdout.write("\n")
        self.stdout.write("Henter dirlisting fra S3, vennligst vent...\n")

        for key in buck.list(prefix=settings.AWS_IMAGEGALLERY_PREFIX):
            if key.name == settings.AWS_IMAGEGALLERY_PREFIX:
                continue

            # Filter out thumbs
            if any(key.name.find('-%s.' % thumb) != -1 for thumb in settings.THUMB_SIZES):
                continue

            image_key = re.sub(settings.AWS_IMAGEGALLERY_PREFIX, '', key.name[:key.name.rfind('.')])
            if not Image.objects.filter(key=image_key).exists():
                ghost_keys.append(key)


        if len(ghost_keys) == 0:
            self.stdout.write("Fant ingen ghost images!\n")
            return

        self.stdout.write("Fant %s ghost images:\n" % len(ghost_keys))
        self.stdout.write("\n")

        for key in ghost_keys:
            content_check = ''
            if Content.objects.filter(content__icontains=key.name).exists():
                list_ids = Content.objects.filter(content__icontains=key.name).values_list('id', flat=True)
                list_str = ', '.join([str(id) for id in list_ids])
                content_check = " -- ADVARSEL, bildet er brukt i Content-felter med id: %s" % list_str
            self.stdout.write("  http://%s/%s%s\n" % (s3_bucket(), key.name, content_check))
        self.stdout.write("\n")

        if raw_input("Slett dem? (y/N) ") != 'y':
            self.stdout.write("Avbryter.\n")
            return

        self.stdout.write("Sletter %s bilder (%s filer inkl. thumbs), vennligst vent...\n" % (len(ghost_keys), len(ghost_keys) * (len(settings.THUMB_SIZES) + 1)))

        for key in ghost_keys:
            key.delete()
            for size in settings.THUMB_SIZES:
                name, extension = key.name.rsplit('.', 1)
                thumb_key = "%s-%s.%s" % (name, size, extension)
                buck.get_key(thumb_key).delete()

        self.stdout.write("\n")
        self.stdout.write("Done.\n")
