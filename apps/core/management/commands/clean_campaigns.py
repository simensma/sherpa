# encoding: utf-8
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import boto

from admin.models import Campaign
from core.util import s3_bucket

class Command(BaseCommand):
    args = u""
    help = u"Fjerner bilder i kampanjebilde-mappa på S3 som ikke er referert i databasen lengre"

    def handle(self, *args, **options):
        if raw_input("Du bør kun kjøre dette scriptet på produksjonsserveren.\nSkriv 'prod' for vise at du vet hva du gjør: ") != 'prod':
            self.stdout.write("Avbryter.\n")
            return

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        buck = conn.get_bucket(s3_bucket())

        ghost_keys = []

        self.stdout.write("\n")
        self.stdout.write("Henter dirlisting fra S3, vennligst vent...\n")

        for key in buck.list(prefix=settings.AWS_CAMPAIGNS_PREFIX):
            if key.name == '%s/' % settings.AWS_CAMPAIGNS_PREFIX:
                continue

            image_hash = re.sub(settings.AWS_CAMPAIGNS_PREFIX, '', key.name[:key.name.rfind('.')])
            if not Campaign.objects.filter(image_cropped_hash=image_hash).exists():
                ghost_keys.append(key)


        if len(ghost_keys) == 0:
            self.stdout.write("Fant ingen ghost images!\n")
            return

        self.stdout.write("Fant %s ghost images:\n" % len(ghost_keys))
        self.stdout.write("\n")

        for key in ghost_keys:
            self.stdout.write("  http://%s/%s\n" % (s3_bucket(), key.name))
        self.stdout.write("\n")

        if raw_input("Slett dem? (y/N) ") != 'y':
            self.stdout.write("Avbryter.\n")
            return

        self.stdout.write("Sletter %s bilder, vennligst vent...\n" % len(ghost_keys))

        for key in ghost_keys:
            key.delete()

        self.stdout.write("\n")
        self.stdout.write("Done.\n")
