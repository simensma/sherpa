# encoding: utf-8
from __future__ import print_function

from django.core.management.base import BaseCommand

from page.models import *

class Command(BaseCommand):
    args = u""
    help = u"Erstatt en string med en annen i all type innhold"

    def handle(self, *args, **options):
        print()
        print("Dette scriptet lar deg erstatte en tekststreng med en annen, typisk nyttig")
        print("hvis et nettsted har lansert sin hjemmeside og du vil automatisk oppdatere")
        print("alle lenker og referanser til URL-adressen.")
        print()
        print("Vzr obs på at dette vil erstatter ALT innhold som matcher strengen du skriver inn.")

        string = raw_input("Gammel tekststreng: ")
        replacement = raw_input("Erstattes med: ")
        print()

        # Very basic safeguard
        if len(string) < 4:
            print("Strengen '%s' er veldig kort og det kan hende den matcher mer enn du tror." % string)
            if raw_input("Sikker på at du vil fortsette? (y/N) ") != 'y':
                print("Avbryter.")
                return
            print()

        print("Gammel streng: '%s'" % string)
        print("Erstattes med: '%s'" % replacement)
        print("Tilsvarer:     re.sub(%s, %s, <innhold>)" % (string, replacement))
        print()
        print("Vil erstattes i alt innhold (sider og artikler), samt i URLer i toppmenyen.")
        print()

        if raw_input("Ser dette riktig ut? (y/N) ") != 'y':
            print("Avbryter.")
            return

        # Replace in all content
        print("Erstatter innhold...")
        for content in Content.objects.all():
            if string in content.content:
                content.content = re.sub(string, replacement, content.content)
                content.save()

        # Replace all menu URLs
        print("Erstatter menyer...")
        for menu in Menu.objects.all():
            if string in menu.url:
                menu.url = re.sub(string, replacement, menu.url)
                menu.save()
        print("Done.")
