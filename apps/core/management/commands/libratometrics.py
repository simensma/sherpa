# encoding: utf-8
from django.core.management.base import BaseCommand

import json

from user.models import User, Permission
from fjelltreffen.models import Annonse

class Command(BaseCommand):
    args = u""
    help = u"Henter sherpa-metrics for libratoappen vår, se https://github.com/Turistforeningen/librato"

    def handle(self, *args, **options):
        users = User.objects.filter(is_active=True)
        inactive_users = User.objects.filter(is_active=False)
        sherpa_users = users.filter(permissions=Permission.objects.get(name='sherpa'))
        metrics = {
            'gauges': [{
                'name': 'sherpa.db.users',
                'value': users.count()
            }, {
                'name': 'sherpa.db.inactive_users',
                'value': inactive_users.count()
            }, {
                'name': 'sherpa.db.sherpa_users',
                'value': sherpa_users.count()
            }, {
                'name': 'sherpa.db.fjelltreffen_annonser',
                'value': Annonse.objects.count()
            }, {
                'name': 'sherpa.db.fjelltreffen_annonser_aktive',
                'value': Annonse.get_active().count()
            }],
            'counters': []
        }

        self.stdout.write(json.dumps(metrics))
