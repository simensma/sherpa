# encoding: utf-8
from django.core.management.base import BaseCommand

from focus.models import Actor, Enrollment
from user.models import User

import logging

logger = logging.getLogger('sherpa')

class Command(BaseCommand):
    args = u""
    help = u"Updates users statuses according to Focus"

    def handle(self, *args, **options):

        members = User.objects.filter(memberid__isnull=False)
        pending_users = members.filter(is_pending=True)
        normal_users = members.filter(is_pending=False)

        # Check for pending users that recently got their Actor, and shouldn't be pending
        for u in pending_users.filter(is_expired=False):
            # This method automatically updates the user if not pending anymore
            u.verify_still_pending(ignore_cache=True)

        # Check for expired pending users that may have gotten their Actor or Enrollment object back
        # (doesn't make sense that this actually happens, but let's not make assumptions for Focus)
        for u in pending_users.filter(is_expired=True):
            if Actor.objects.filter(memberid=u.memberid).exists():
                u.is_expired = False
                u.is_pending = False
                u.save()
            elif Enrollment.objects.filter(memberid=u.memberid).exists():
                u.is_expired = False
                u.save()

        # Check for normal expired users that regained their Actor and shouldn't be expired anymore
        for u in normal_users.filter(is_expired=True):
            if Actor.objects.filter(memberid=u.memberid).exists():
                u.is_expired = False
                u.save()

        # Check for normal users that have lost their Actor and should be expired
        for u in normal_users.filter(is_expired=False):
            if not Actor.objects.filter(memberid=u.memberid).exists():
                u.is_expired = True
                u.save()
