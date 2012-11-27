# encoding: utf-8
from django.core.management.base import BaseCommand
from core.models import Zipcode, ZipcodeState
from focus.models import FocusZipcode
from datetime import datetime
import re

# Note: Does not compare the state of the DB to the files - simply lists the changes based on last update in ZipcodeState.

class ZipcodeNew():
    def __init__(self, zipcode, area, city_code, city, date):
        self.zipcode = zipcode
        self.area = area
        self.city_code = city_code
        self.city = city
        self.date = date

class ZipcodeChange():
    def __init__(self, old_zipcode, old_area, new_zipcode, new_area, date):
        self.old_zipcode = old_zipcode
        self.old_area = old_area
        self.new_zipcode = new_zipcode
        self.new_area = new_area
        self.date = date

class ZipcodeRemoval():
    def __init__(self, zipcode, area, date):
        self.zipcode = zipcode
        self.area = area
        self.date = date

class Command(BaseCommand):
    args = u'<check|report|sync|focus>'
    help = u'Rapporterer og utfører endringer i postens postnummerregister'

    def handle(self, *args, **options):


        if len(args) == 0:
            args = ['check']

        if args[0] == 'check':
            if not self.parse_registers():
                return
            self.stdout.write("Endringer siden %s:\n" % self.last_update)
            self.stdout.write(" - %s nye postnumre\n" % len(self.to_be_created))
            self.stdout.write(" - %s endrede postnumre\n" % len(self.to_be_changed))
            self.stdout.write(" - %s slettede postnumre\n" % len(self.to_be_removed))
            self.stdout.write("\n")
            self.stdout.write("Kjør med 'report' for fullstendig rapport (kan bli lang)\n")
            self.stdout.write("Kjør med 'sync' for å oppdatere databasen automatisk\n")

        elif args[0] == 'report':
            if not self.parse_registers():
                return
            self.stdout.write("Postnummerendringer siden %s:\n\n" % self.last_update)

            self.stdout.write("Nye:\n")
            for p in self.to_be_created:
                self.stdout.write("%s %s %s %s\n" % (p.zipcode, p.area, p.city_code, p.city))
            self.stdout.write("\n")

            self.stdout.write("Endret:\n")
            for p in self.to_be_changed:
                self.stdout.write("%s %s -> %s %s\n" % (p.old_zipcode, p.old_area, p.new_zipcode, p.new_area))
            self.stdout.write("\n")

            self.stdout.write("Slettet:\n")
            for p in self.to_be_removed:
                self.stdout.write("%s %s\n" % (p.zipcode, p.area))


        elif args[0] == 'sync':
            if not self.parse_registers():
                return
            self.stdout.write(" - %s nye postnumre vil legges inn\n" % len(self.to_be_created))
            self.stdout.write(" - %s postnumre vil endres\n" % len(self.to_be_changed))
            self.stdout.write(" - %s postnumre skal slettes, men SLETTES IKKE AUTOMATISK\n" % len(self.to_be_removed))
            self.stdout.write("\n")

            if raw_input("Fortsett? (y/n) ") == 'y':

                self.stdout.write("(1/2) Legger inn nye postnumre...\n")
                for nz in self.to_be_created:
                    z = Zipcode(
                        zipcode=nz.zipcode,
                        area=nz.area,
                        city_code=nz.city_code,
                        city=nz.city)
                    z.save()

                self.stdout.write("(2/2) Oppdaterer eksisterende postnumre...\n")
                for cz in self.to_be_changed:
                    z = Zipcode.objects.get(zipcode=cz.old_zipcode, area=cz.old_area)
                    z.zipcode = cz.new_zipcode
                    z.area = cz.new_area
                    z.save()

                state = ZipcodeState.objects.all()[0]
                state.last_update = datetime.now()
                state.save()

                self.stdout.write("\n")
                self.stdout.write("Postnummerdatabasen har blitt synkronisert!\n")

                if len(self.to_be_removed) > 0:
                    self.stdout.write("Du bør slette følgende numre manuelt:\n")
                    self.stdout.write("\n")

                    for rz in self.to_be_removed:
                        self.stdout.write("  %s %s\n" % (rz.zipcode, rz.area))

                    self.stdout.write("\n")
                    self.stdout.write("Hvis du har relasjoner til andre tabeller bør du sjekke om det finnes noen knytning til hver av disse.\n")
                    self.stdout.write("Hvis noen slike finnes er jeg ikke helt sikker på hva fremgangsmåten er - det må du finne ut av!\n")
                    self.stdout.write("\n")
                    self.stdout.write("Merk: Disse postnumrene vil ikke listes ved neste sync, fordi last_update er satt til \"nå\"\n")

        elif args[0] == 'focus':
            self.stdout.write("Følgende er i vår database men ikke i Focus:\n")
            missing = Zipcode.objects.exclude(zipcode__in=[z['zipcode'] for z in FocusZipcode.objects.all().values('zipcode')]).order_by('zipcode')
            for z in missing:
                self.stdout.write("%s %s %s %s\n" % (z.zipcode, z.area, z.city_code, z.city))
            self.stdout.write("\n")

            self.stdout.write("Totalt %s manglende postnumre.\n" % len(missing))

    def parse_registers(self):
        self.stdout.write("Parser postnummerregistre, vennligst vent...\n\n")

        filename_new = 'postnummerlogg_nye_ansi.txt'
        filename_changes = 'postnummerlogg_endringer_ansi.txt'
        try:
            with open(filename_new, 'rt') as f:
                self.new_zipcodes = list()
                for line in f:
                    line = line.decode('iso-8859-1')
                    m = re.match('^(\d{4})\t(.*)\t(\d{4})\t(.*)\t\d{3}\t(\d{2})\t(\d{2})\t(\d{2})\t(\d{2})', line)
                    if m:
                        g = m.groups(0)
                        date = datetime(day=int(g[4]), month=int(g[5]), year=int(g[6] + g[7]))
                        self.new_zipcodes.append(ZipcodeNew(g[0], g[1], g[2], g[3], date))
                    else:
                        self.stdout.write("Error: Klarte ikke å parse følgende linje i '%s':\n" % filename_new)
                        self.stdout.write("  -> '%s'\n" % line.strip())
                        self.stdout.write("Sjekk om det er nytt format i postnummerregisterfilene. Du må kanskje inn og oppdatere zipcode-kommandoen :)\n")
                        return False

            with open(filename_changes, 'rt') as f:
                self.changed_zipcodes = list()
                self.removed_zipcodes = list()
                for line in f:
                    line = line.decode('iso-8859-1')
                    m = re.match('^(\d{4})\t(.*)\t(\d{2})\t(\d{2})\t(\d{2})\t(\d{2})\t(\d{4})\t(.*)\t(\w)\t(\w)', line)
                    if not m:
                        m = re.match('^(\d{4})\t(.*)\t(\d{2})\t(\d{2})\t(\d{2})\t(\d{2})\t(\d{4})\t(.*?)\t', line)
                    if m:
                        g = m.groups(0)
                        date = datetime(day=int(g[2]), month=int(g[3]), year=int(g[4] + g[5]))
                        if g[6] != '9999':
                            # Skip if only 'category' is changed, we don't record category
                            if len(g) > 8 and g[0] == g[6] and g[1] == g[7] and g[8] != g[9]:
                                continue
                            self.changed_zipcodes.append(ZipcodeChange(g[0], g[1], g[6], g[7], date))
                        else:
                            self.removed_zipcodes.append(ZipcodeRemoval(g[0], g[1], date))
                    else:
                        self.stdout.write("Error: Klarte ikke å parse følgende linje i '%s':\n" % filename_changes)
                        self.stdout.write("  -> '%s'\n" % line.strip())
                        self.stdout.write("Sjekk om det er nytt format i postnummerregisterfilene. Du må kanskje inn og oppdatere zipcode-kommandoen :)\n")
                        return False

            self.last_update = ZipcodeState.objects.all()[0].last_update
            self.to_be_created = [nz for nz in self.new_zipcodes if nz.date > self.last_update]
            self.to_be_changed = [nz for nz in self.changed_zipcodes if nz.date > self.last_update]
            self.to_be_removed = [nz for nz in self.removed_zipcodes if nz.date > self.last_update]

            return True

        except IOError:
             self.stdout.write("Forventet å finne følgende filer i denne mappa:\n")
             self.stdout.write("  '%s' (Oversikt over alle nye postnummer med TAB-separerte felter, ANSI).\n" % filename_new)
             self.stdout.write("  '%s' (Oversikt over alle endringer med TAB-separerte felter, ANSI).\n" % filename_changes)
             self.stdout.write("Last dem ned herfra: http://www.bring.no/144754/postnummertabeller\n")
             return False

