# encoding: utf-8
from django.core.management.base import BaseCommand

from focus.models import Actor
from user.models import User

import logging

logger = logging.getLogger('sherpa')

class Command(BaseCommand):
    args = u""
    help = u"Checks if pending users are still pending, and automatically updates them if not"

    def handle(self, *args, **options):
        for u in User.objects.filter(is_pending=True):
            # This method automatically updates the user if not pending anymore
            u.verify_still_pending()
