# encoding: utf-8
from django.contrib import messages

from datetime import datetime

from core.models import Zipcode
from core import validator

# Gift-membership-types
membership_types = [
  {'code': 'normal', 'name': 'Vanlig medlemskap', 'price': None},
  {'code': 'baptism', 'name': 'Dåpsgave', 'price': 1000},
  {'code': 'jubilee', 'name': 'Jubileum', 'price': 5700},
  {'code': 'life', 'name': 'Livsvarig medlemskap', 'price': 14250},
]

membership_price_by_code = {type['code']: type['price'] for type in membership_types}

# Not a DB-model! Used in session for gift memberships
class Giver():
    def __init__(self, name, address, zipcode, memberid, phone, email):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        try:
            self.area = Zipcode.objects.get(zipcode=zipcode).area
        except Zipcode.DoesNotExist:
            # We'll let empty area define invalid zipcode in this case.
            self.area = ''
        self.memberid = memberid
        self.phone = phone
        self.email = email

    def validate(self, request=None, add_messages=False):
        valid = True

        if not validator.name(self.name):
            if add_messages:
                messages.error(request, u"Du har glemt å skrive inn navnet ditt.")
            valid = False

        if not validator.address(self.address):
            if add_messages:
                messages.error(request, u"Du må oppgi din egen adresse da vi sender faktura og medlemskort hjem til deg.")
            valid = False

        if not validator.zipcode(self.zipcode) or self.area == '':
            # Empty area defines invalid zipcode, as stated in __init__
            if add_messages:
                messages.error(request, u"Postnummeret ditt ser ikke riktig ut. Du må oppgi et gyldig postnummer da vi sender faktura og medlemskort hjem til deg.")
            valid = False

        if not validator.memberid(self.memberid, req=False):
            if add_messages:
                messages.error(request, u"Medlemsnummeret ditt kan kun bestå av tall. Du trenger ikke være medlem for å bestille gavemedlemskap, da kan du la medlemsnummerfeltet stå tomt.")
            valid = False

        if not validator.phone(self.phone, req=False):
            if add_messages:
                messages.error(request, u"Telefonnummeret ditt må være minst 8 siffer. Du trenger ikke oppgi telefonnummeret ditt, men vi anbefaler at du gir oss minst én måte å kontakte deg.")
            valid = False

        if not validator.email(self.email, req=False):
            if add_messages:
                messages.error(request, u"E-postadressen din er ikke en gyldig adresse. Du trenger ikke oppgi e-postadressen din, men vi anbefaler at du gir oss minst én måte å kontakte deg.")
            valid = False

        return valid

# Not a DB-model! Used in session for gift memberships
class Receiver():
    def __init__(self, type, name, dob, address, zipcode, phone, email):
        self.type_index = int(type)
        self.type = membership_types[self.type_index]
        self.name = name
        try:
            self.dob = datetime.strptime(dob, "%d.%m.%Y")
        except ValueError:
            self.dob = None
        self.address = address
        self.zipcode = zipcode
        try:
            self.area = Zipcode.objects.get(zipcode=zipcode).area
        except Zipcode.DoesNotExist:
            self.area = ''
        self.phone = phone
        self.email = email

    def validate(self, request=None, add_messages=False):
        valid = True

        if self.type_index < 0 or self.type_index >= len(membership_types):
            if add_messages:
                messages.error(request, u"Du har på en eller annen måte klart å angi en ugyldig medlemskapstype. Vennligst bruk select-boksen til å velge medlemskapstype.")
            valid = False

        if not validator.name(self.name):
            if add_messages:
                if len(self.name) > 0:
                    messages.error(request, u"Du må angi fullt navn til %s." % self.name)
                else:
                    messages.error(request, u"En av mottakerne mangler navn.")
            valid = False

        if not isinstance(self.dob, datetime):
            if add_messages:
                messages.error(request, u"Fødselsdatoen til %s er ugyldig." % self.name)
            valid = False

        if isinstance(self.dob, datetime) and self.dob >= datetime.now():
            if add_messages:
                messages.error(request, u"Fødselsdatoen til %s kan ikke være i fremtiden." % self.name)
            valid = False

        if not validator.address(self.address):
            if add_messages:
                messages.error(request, u"%s mangler adresse." % self.name)
            valid = False

        if not validator.zipcode(self.zipcode) or self.area == '':
            if add_messages:
                messages.error(request, u"Postnummeret til %s er mangler eller er feil." % self.name)
            valid = False

        if not validator.phone(self.phone, req=False):
            if add_messages:
                messages.error(request, u"Telefonnummeret til %s må bestå av minst 8 siffer." % self.name)
            valid = False

        if not validator.email(self.email, req=False):
            if add_messages:
                messages.error(request, u"E-postadressen til %s er ikke gyldig." % self.name)
            valid = False

        return valid
