# encoding: utf-8
from django.core.management.base import BaseCommand

from focus.models import Enrollment

import logging

logger = logging.getLogger('sherpa')

#
# NOTE that we recently changed the payment_method column datatype from float to int, and suspect that
# will fix this bug. We'll let the command run in crontab for some time, but if you're checking out this
# file in year 2016 or something and no bugs have been reported it's probably safe to delete this command.
#
class Command(BaseCommand):
    args = u""
    help = u"Sjekker for heisenbugs med focus.Enrollment.payment_method"

    def handle(self, *args, **options):

        # We've already handled and ignored this error for the following memberids:
        known_fails = [4627636, 4810742, 5031284, 5031291, 5105701]

        # Check for new ones
        new_fails = Enrollment.objects.filter(paid=True, payment_method=0).exclude(memberid__in=known_fails)

        if new_fails.count() > 0:
            logger.error(u"Fant en ny innmelding med paid=True og payment_method=0",
                extra={
                    'memberids': [e.memberid for e in new_fails]
                }
            )
