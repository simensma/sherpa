# encoding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings

import sys

from datetime import datetime, timedelta
import boto

class Command(BaseCommand):
    args = u"manual | auto"
    help = u"Fjerner utgåtte versjonsobjekter i S3"

    def handle(self, *args, **options):
        if len(args) < 1:
            args = ['manual']

        if args[0] not in ['manual', 'auto']:
            self.stdout.write("Feil argument, prøv 'help cleans3'.\n")
            return

        AGE_LIMIT_DAYS = 365

        if args[0] == 'manual':
            sys.stdout.write("Søker etter %s dager gamle objekter...\n\n" % AGE_LIMIT_DAYS)

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        buck = conn.get_bucket(settings.AWS_BUCKET)

        then = datetime.utcnow() - timedelta(hours=(24 * AGE_LIMIT_DAYS))
        versions_to_delete = []
        active_keys = 0
        backup_versions = 0

        for v in buck.list_versions():
            # Getting the key again like this is very slow, but we don't run this script
            # often, so it'll work for now.
            if v.version_id == buck.get_key(v.name).version_id:
                # This is the current version, don't you dare to anything to it.
                active_keys += 1
                continue

            mod = datetime.strptime(v.last_modified, '%Y-%m-%dT%H:%M:%S.000Z')
            if mod < then:
                versions_to_delete.append({
                    'key': v.name,
                    'version_id': v.version_id
                })
            else:
                backup_versions += 1

        if args[0] == 'manual':
            sys.stdout.write("%s aktive objekter\n" % active_keys)
            sys.stdout.write("%s backup-versjoner (yngre enn %s dager)\n" % (backup_versions, AGE_LIMIT_DAYS))
            sys.stdout.write("%s gamle versjoner til sletting\n\n" % len(versions_to_delete))

            if len(versions_to_delete) == 0:
                return

            if raw_input("Slett %s gamle versjonsobjekter fra S3 permanent? (y/n): " % len(versions_to_delete)) != 'y':
                self.stdout.write("Avbryter.\n")
                return

        for v in versions_to_delete:
            buck.delete_key(v['key'], version_id=v['version_id'])
