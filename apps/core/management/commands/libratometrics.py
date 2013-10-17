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

        # Count all expired users as expired (regardless of pending etc),
        # and all non-expired pending users as pending (regardless of active/inactive).

        users = User.objects.all()
        active_users = users.filter(is_inactive=False, is_expired=False, is_pending=False)
        inactive_users = users.filter(is_inactive=True, is_expired=False, is_pending=False)
        pending_users = users.filter(is_expired=False, is_pending=True)
        expired_users = users.filter(is_expired=True)
        normal_users = active_users.exclude(permissions=Permission.objects.get(name='sherpa'))
        sherpa_users = active_users.filter(permissions=Permission.objects.get(name='sherpa'))

        # Fjelltreffen
        ft_active_period = date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)
        ft_active_published = Annonse.objects.filter(date_renewed__gte=ft_active_period, hidden=False).count()
        ft_active_hidden = Annonse.objects.filter(date_renewed__gte=ft_active_period, hidden=True).count()
        ft_inactive = Annonse.objects.filter(date_renewed__lt=ft_active_period).count()

        metrics = {
            'gauges': [{
                'name': 'sherpa.db.users',
                'value': normal_users.count()
            }, {
                'name': 'sherpa.db.inactive_users',
                'value': inactive_users.count()
            }, {
                'name': 'sherpa.db.expired_users',
                'value': expired_users.count()
            }, {
                'name': 'sherpa.db.pending_users',
                'value': pending_users.count()
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
