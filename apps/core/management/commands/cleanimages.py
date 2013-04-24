# encoding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings

import simples3
import re

from admin.models import Image
from page.models import Content

class Command(BaseCommand):
    args = u""
    help = u"Fjerner bilder i bildearkiv-mappa på S3 som ikke er referert i databasen lengre"

    def handle(self, *args, **options):
        if raw_input("Du bør kun kjøre dette scriptet på produksjonsserveren.\nSkriv 'prod' for vise at du vet hva du gjør: ") != 'prod':
            self.stdout.write("Avbryter.\n")
            return

        s3 = simples3.S3Bucket(
            settings.AWS_BUCKET,
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY,
            'https://%s' % settings.AWS_BUCKET)

        ghost_keys = []

        self.stdout.write("\n")
        self.stdout.write("Henter dirlisting fra S3, vennligst vent...\n")

        for (aws_key, modify, etag, size) in s3.listdir(prefix=settings.AWS_IMAGEGALLERY_PREFIX):
            if aws_key == settings.AWS_IMAGEGALLERY_PREFIX:
                continue

            # Filter out thumbs
            filename, extension = aws_key.rsplit('.', 1)
            if any(filename.endswith('-%s' % thumb) for thumb in settings.THUMB_SIZES):
                continue

            key = re.sub(settings.AWS_IMAGEGALLERY_PREFIX, '', filename)

            if not Image.objects.filter(key=key).exists():
                ghost_keys.append((filename, extension))

        if len(ghost_keys) == 0:
            self.stdout.write("Fant ingen ghost images!\n")
            return

        self.stdout.write("Fant %s ghost images:\n" % len(ghost_keys))
        self.stdout.write("\n")

        for key, extension in ghost_keys:
            content_check = ''
            if Content.objects.filter(content__icontains=key).exists():
                list_ids = Content.objects.filter(content__icontains=key).values_list('id', flat=True)
                list_str = ', '.join([str(id) for id in list_ids])
                content_check = " -- ADVARSEL, bildet er brukt i Content-felter med id: %s" % list_str
            self.stdout.write("  http://%s/%s.%s%s\n" % (settings.AWS_BUCKET, key, extension, content_check))
        self.stdout.write("\n")

        if raw_input("Slett dem? (y/N) ") != 'y':
            self.stdout.write("Avbryter.\n")
            return

        def delete_image(key, extension):
            s3.delete("%s.%s" % (key, extension))
            for size in settings.THUMB_SIZES:
                s3.delete("%s-%s.%s" % (key, str(size), extension))

        self.stdout.write("Sletter %s bildefiler (inkl. thumbs), vennligst vent...\n" % (len(ghost_keys) * (len(settings.THUMB_SIZES) + 1)))

        for key, extension in ghost_keys:
            delete_image(key, extension)

        self.stdout.write("\n")
        self.stdout.write("Done.\n")
