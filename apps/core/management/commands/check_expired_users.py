# encoding: utf-8
from django.core.management.base import BaseCommand

from focus.models import Actor
from user.models import User

import logging

logger = logging.getLogger('sherpa')

class Command(BaseCommand):
    args = u""
    help = u"Verifies that expired users are expired"

    def handle(self, *args, **options):
        # Check for newly expired users - will take a while
        hits = []
        for u in User.objects.filter(memberid__isnull=False, is_expired=False):
            if not Actor.objects.filter(memberid=u.memberid).exists():
                u.is_expired = True
                u.save()
                hits.append(u.memberid)

        if len(hits) > 0:
            logger.warning(u"Bruker(e) med medlemsnummer finnes ikke i Focus - setter is_expired til True",
                extra={
                    'memberids': hits
                }
            )

        # Verify that expired users are expired
        hits = []
        for u in User.objects.filter(memberid__isnull=False, is_expired=True):
            if Actor.objects.filter(memberid=u.memberid).exists():
                hits.append(u.memberid)

        if len(hits) > 0:
            logger.warning(u"Utgåtte brukere *finnes* i Focus igjen - sjekk opp hva som har skjedd",
                extra={
                    'memberids': hits
                }
            )
