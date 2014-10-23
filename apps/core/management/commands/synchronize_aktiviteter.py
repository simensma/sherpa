# encoding: utf-8
from django.core.management.base import BaseCommand

from sherpa2.models import Activity

class Command(BaseCommand):
    args = u""
    help = u"Synkroniserer alle aktiviteter fra gamle Sherpa til nye - kjøres vanligvis kun av crontab"

    def handle(self, *args, **options):
        Activity.sync_all()
