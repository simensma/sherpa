# encoding: utf-8
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission

import json

from user.models import Profile
from fjelltreffen.models import Annonse

class Command(BaseCommand):
    args = u""
    help = u"Henter sherpa-metrics for libratoappen vår, se https://github.com/Turistforeningen/librato"

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        sherpa_profiles = profiles.filter(user__user_permissions=Permission.objects.get(codename='sherpa'))
        metrics = {
            'gauges': [{
                'name': 'sherpa.db.users',
                'value': profiles.count()
            }, {
                'name': 'sherpa.db.sherpa_users',
                'value': sherpa_profiles.count()
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
