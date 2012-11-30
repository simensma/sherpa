# encoding: utf-8
from django.core.management.base import BaseCommand
from core.models import Site

class Command(BaseCommand):
    args = u'<domene1> <domene2>'
    help = u"Endrer domene på for en gitt Site"

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stdout.write("Du må angi to domener.\n")
            return

        s = Site.objects.get(domain=args[0])
        s.domain = args[1]
        s.save()
        self.stdout.write("Endret '%s' til '%s'\n" % (args[0], args[1]))
