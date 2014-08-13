# encoding: utf-8
from __future__ import print_function

import sys

from django.core.management.base import BaseCommand
from django.conf import settings

import boto

class Command(BaseCommand):
    args = u""
    help = u"Synkroniser S3 utviklingsmiljø med prod"

    def handle(self, *args, **options):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        prod_bucket = conn.get_bucket(settings.AWS_BUCKET)
        dev_bucket = conn.get_bucket(settings.AWS_BUCKET_DEV)

        # First iterate the development-bucket, overwriting existing modified files and deleting deleted files
        print("Iterating the dev-bucket to find updated or deleted keys...")
        updated_keys = 0
        deleted_keys = 0
        confirmed_keys = []
        for dev_key in dev_bucket.list():
            # Show progress for each processed key
            print(".", end="")
            sys.stdout.flush()

            prod_key = prod_bucket.get_key(dev_key.name)

            # Deleted?
            if prod_key is None:
                deleted_keys += 1
                dev_key.delete()
                continue

            # Since we know that this key exists on dev, save it for later
            confirmed_keys.append(dev_key.name)

            # Changed?
            if dev_key.size != prod_key.size or dev_key.etag != prod_key.etag:
                updated_keys += 1
                prod_key.copy(dev_bucket.name, prod_key.name, preserve_acl=True)
                continue

        print("\nDone: %s keys updated, %s keys deleted" % (updated_keys, deleted_keys))

        # Then iterate the production bucket, and copy over any new files
        print()
        print("Iterating the production-bucket to find new keys (%s confirmed keys will be skipped)..." % len(confirmed_keys))
        new_keys = 0
        for prod_key in prod_bucket.list():
            # Show progress for each processed key
            print(".", end="")
            sys.stdout.flush()

            # If we already confirmed this key in the dev-bucket, skip it
            if prod_key.name in confirmed_keys:
                continue

            dev_key = dev_bucket.get_key(prod_key.name)

            # New?
            if dev_key is None:
                new_keys += 1
                prod_key.copy(dev_bucket.name, prod_key.name, preserve_acl=True)
                continue

            # Don't check for changes if it exists - this has already been checked when iterating the dev-bucket

        print("\nDone: %s keys created." % new_keys)
