# encoding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import date, timedelta
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

        # Fjelltreffen
        ft_active_period = date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)
        ft_active_published = Annonse.objects.filter(date_renewed__gte=ft_active_period, hidden=False).count()
        ft_active_hidden = Annonse.objects.filter(date_renewed__gte=ft_active_period, hidden=True).count()
        ft_inactive = Annonse.objects.filter(date_renewed__lt=ft_active_period).count()

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
                'name': 'sherpa.db.fjelltreffen.annonser.active.published',
                'value': ft_active_published
            }, {
                'name': 'sherpa.db.fjelltreffen.annonser.active.hidden',
                'value': ft_active_hidden
            }, {
                'name': 'sherpa.db.fjelltreffen.annonser.inactive',
                'value': ft_inactive
            }],
            'counters': []
        }

        self.stdout.write(json.dumps(metrics))
