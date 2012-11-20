# encoding: utf-8
from django.db import models

from datetime import datetime

from page.models import Variant
from core.models import Zipcode

from core import validator

# Has always only *one* row
class State(models.Model):
    active = models.BooleanField()
    card = models.BooleanField() # Accept card-payment


# Gift-membership-types
membership_types = [
  {'name': 'Vanlig medlemskap', 'price': None},
  {'name': 'Dåpsgave', 'price': 900},
  {'name': 'Jubileum', 'price': 5500},
  {'name': 'Livsvarig medlemskap', 'price': 13750},
]

# Not a DB-model! Used in session for gift memberships
class Giver():
    def __init__(self, name, address, zipcode, memberno, phone, email):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        try:
            self.area = Zipcode.objects.get(zipcode=zipcode).area
        except Zipcode.DoesNotExist:
            self.area = ''
        self.memberno = memberno
        self.phone = phone
        self.email = email

    def validate(self):
        if not validator.name(self.name):
            return False

        if not validator.address(self.address):
            return False

        if not validator.zipcode(self.zipcode):
            return False

        if self.area == '':
            return False

        if not validator.memberno(self.memberno, req=False):
            return False

        if not validator.phone(self.phone, req=False):
            return False

        if not validator.email(self.email, req=False):
            return False

        if not Zipcode.objects.filter(zipcode=self.zipcode).exists():
            return False

        return True

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

    def validate(self):
        if self.type_index < 0 or self.type_index >= len(membership_types):
            return False

        if not validator.name(self.name):
            return False

        if not isinstance(self.dob, datetime):
            return False

        if not validator.address(self.address):
            return False

        if not validator.zipcode(self.zipcode):
            return False

        if self.area == '':
            return False

        if not validator.phone(self.phone, req=False):
            return False

        if not validator.email(self.email, req=False):
            return False

        if not Zipcode.objects.filter(zipcode=self.zipcode).exists():
            return False

        return True
