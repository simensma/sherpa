# encoding: utf-8
from datetime import datetime
import logging
import sys

from django.core.management.base import BaseCommand

from aktiviteter.models import SynchronizationDate
from sherpa2.models import Activity

logger = logging.getLogger('sherpa')

class Command(BaseCommand):
    args = u""
    help = u"Synkroniserer alle aktiviteter fra gamle Sherpa til nye - kjøres vanligvis kun av crontab"

    def handle(self, *args, **options):
        try:
            Activity.synchronize()
            date = SynchronizationDate.objects.get()
            date = datetime.now()
            date.save()
        except:
            logger.error(u"Uhåndtert exception ved synkronisering av aktiviteter",
                exc_info=sys.exc_info(),
            )
