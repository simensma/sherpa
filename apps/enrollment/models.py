# encoding: utf-8
from django.db import models, transaction, connections
from django.core.cache import cache

from core import validator
from core.models import FocusCountry
from foreninger.models import Forening

from focus.models import Price, Enrollment as FocusEnrollment

from focus.util import PAYMENT_METHOD_CODES, get_membership_type_by_codename
from enrollment.util import AGE_SENIOR, AGE_MAIN, AGE_YOUTH, AGE_SCHOOL, KEY_PRICE, FOREIGN_SHIPMENT_PRICE
from core.util import membership_year_start

from datetime import date
import random

# Has always only *one* row
class State(models.Model):
    active = models.BooleanField()
    card = models.BooleanField() # Accept card-payment

    def __unicode__(self):
        return u'%s (active: %s, card: %s)' % (self.pk, self.active, self.card)

class Enrollment(models.Model):
    STATE_CHOICES = (
        ('registration', 'Registrering'),
        ('payment', 'Til betaling'),
        ('complete', 'Fullført'),
    )
    state = models.CharField(max_length=255)
    accepts_conditions = models.BooleanField()
    existing_memberid = models.CharField(max_length=51)
    wants_yearbook = models.BooleanField()
    attempted_yearbook = models.BooleanField()
    payment_method = models.CharField(max_length=51)
    RESULT_CHOICES = (
        ('success_invoice', 'Faktura bestilt'),
        ('success_card', 'Kortbetaling godkjent'),
        ('fail', 'Kortbetaling ikke godkjent'),
        ('cancel', 'Kortbetaling avbrutt'),
    )
    result = models.CharField(max_length=255)
    forening = models.ForeignKey('foreninger.Forening', null=True, related_name='+')

    # Address information
    country = models.CharField(max_length=2)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    address3 = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=51)
    area = models.CharField(max_length=255)

    date_initiated = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_state(self):
        return [c[1] for c in self.STATE_CHOICES if c[0] == self.state][0]

    def get_result(self):
        return [c[1] for c in self.RESULT_CHOICES if c[0] == self.result][0]

    def get_users_by_name(self):
        return self.users.order_by('name')

    def has_potential_main_member(self):
        return any([user.can_be_main_member() for user in self.users.all()])

    def get_main_or_random_member(self):
        try:
            return self.users.get(chosen_main_member=True)
        except User.DoesNotExist:
            return self.users.all()[0]

    def save_users_to_focus(self):
        if self.existing_memberid != '':
            for user in self.users.all():
                user.save_to_focus(linked_to=self.existing_memberid)

        elif self.has_potential_main_member():
            # Looks like we have a main member, add that one first and the rest as linked to that one
            main_member = self.users.get(chosen_main_member=True)
            child_members = self.users.filter(chosen_main_member=False)

            main_member.save_to_focus()
            for child in child_members:
                child.save_to_focus(main_member.memberid)

        else:
            # In this case, one or more members below youth age are registered,
            # so no main/household relationship applies.
            for user in self.users.all():
                user.save_to_focus()

    def get_country(self):
        return FocusCountry.objects.get(code=self.country)

    def is_applicable_for_dnt_ung_oslo(self):
        """
        Youth members of DNT Oslo og Omegn should be displayed as members of DNT ung Oslo. See
        user.models.User.main_forening() for more information of why we have to create that
        logic here. Use this method to find out how applicable this is for these users
        (applicable for none of them, some, or all).
        """
        if self.forening.id != Forening.DNT_OSLO_ID:
            # Not DNT Oslo og Omegn, applicable for none
            return 'none'
        else:
            if all([u.applicable_for_dnt_ung_oslo() for u in self.users.all()]):
                return 'all'
            elif any([u.applicable_for_dnt_ung_oslo() for u in self.users.all()]):
                return 'some'
            else:
                return 'none'

    def get_actual_forening_if_any(self):
        return self.get_actual_forening(any)

    def get_actual_forening_if_all(self):
        return self.get_actual_forening(all)

    def get_actual_forening(self, desired_count):
        if self.forening.id == Forening.DNT_OSLO_ID and desired_count([u.get_age() < AGE_MAIN and u.get_age() >= AGE_YOUTH for u in self.users.all()]):
            forening = cache.get('forening.%s' % Forening.DNT_UNG_OSLO_ID)
            if forening is None:
                forening = Forening.objects.get(id=Forening.DNT_UNG_OSLO_ID)
                cache.set('forening.%s' % Forening.DNT_UNG_OSLO_ID, forening, 60 * 60 * 24 * 7)
            return forening
        else:
            return self.forening

    def get_prices(self):
        price = cache.get('forening.price.%s' % self.forening.focus_id)
        if price is None:
            price = Price.objects.get(forening_id=self.forening.focus_id)
            cache.set('forening.price.%s' % self.forening.focus_id, price, 60 * 60 * 24 * 7)
        return price

    def get_total_price(self):
        # Calculate the prices and membership type
        total_price = 0
        for user in self.users.all():
            total_price += user.price()
            if user.key:
                total_price += KEY_PRICE

        # Pay for yearbook if foreign. Note that this cannot be set if there are no potential main members
        if self.wants_yearbook:
            total_price += FOREIGN_SHIPMENT_PRICE

        return total_price

    def get_active_transaction(self):
        return self.transactions.get(state='register', active=True)

    def set_active_transaction(self, transaction_id):
        self.transactions.filter(state='register').update(active=False)
        active_transaction = self.transactions.get(state='register', transaction_id=transaction_id)
        active_transaction.active = True
        active_transaction.save()

    @staticmethod
    def get_active():
        return Enrollment.objects.filter(users__isnull=False).distinct()

class User(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='users')
    name = models.CharField(max_length=511)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=511)
    gender = models.CharField(max_length=1)
    key = models.BooleanField()
    dob = models.DateField(null=True)
    chosen_main_member = models.BooleanField()
    memberid = models.IntegerField(null=True)
    pending_user = models.ForeignKey('user.User', related_name='+', null=True)
    sms_sent = models.BooleanField()

    def __unicode__(self):
        return u'%s' % self.pk

    def get_age(self):
        age = date.today().year - self.dob.year

        # After membership year start, the enrollment is really for the next year,
        # hence they'll be one year older than they are this year.
        if date.today() >= membership_year_start()['actual_date']:
            age += 1

        return age

    def can_be_main_member(self):
        return self.get_age() >= AGE_YOUTH

    def is_household_member(self):
        if self.enrollment.existing_memberid != '':
            # There's an existing member, so we're household no matter what
            return True

        if self.enrollment.has_potential_main_member():
            # We have a potential main member in our group, so we'll only be household if
            # we're not the chosen one.
            return not self.chosen_main_member
        else:
            # There's no potential main member in our group (including ourselves), so
            # no main/household status applies.
            return False

    def can_have_yearbook(self):
        # This applies only to foreign members, who can only order the yearbook if they're a main member.
        return not self.is_household_member() and self.can_be_main_member()

    def is_valid(self, require_contact_info=False):
        # Name or address is empty
        if not validator.name(self.name):
            return False

        # Gender is not set
        if self.gender != 'm' and self.gender != 'f':
            return False

        # Use validator for phone number, require only if required
        if not validator.phone(self.phone, req=require_contact_info):
            return False

        # Use validator for email addresss, require only if required
        if not validator.email(self.email, req=require_contact_info):
            return False

        # Date of birth is saved as NULL when invalid
        if self.dob is None:
            return False

        # Birthyear is out of smalldatetime range (MSSQLs datetime datatype will barf)
        if self.dob.year < 1900 or self.dob.year > 2078:
            return False

        # All tests passed!
        return True

    def get_actual_forening(self):
        """
        Return the applicable forening for this user. Which means the default forening in most
        cases, but DNT ung Oslo if the default is DNT Oslo og Omegn and this is a youth member.
        """
        forening = self.enrollment.forening
        if forening.id == Forening.DNT_OSLO_ID and self.applicable_for_dnt_ung_oslo():
            forening = cache.get('forening.%s' % Forening.DNT_UNG_OSLO_ID)
            if forening is None:
                forening = Forening.objects.get(id=Forening.DNT_UNG_OSLO_ID)
                cache.set('forening.%s' % Forening.DNT_UNG_OSLO_ID, forening, 60 * 60 * 24 * 7)
        return forening

    def applicable_for_dnt_ung_oslo(self):
        return self.get_age() < AGE_MAIN and self.get_age() >= AGE_YOUTH

    def membership_type(self):
        if self.is_household_member() and self.get_age() >= AGE_YOUTH:
            return get_membership_type_by_codename('household')['name']
        elif self.get_age() >= AGE_SENIOR:
            return get_membership_type_by_codename('senior')['name']
        elif self.get_age() >= AGE_MAIN:
            return get_membership_type_by_codename('main')['name']
        elif self.get_age() >= AGE_YOUTH:
            return get_membership_type_by_codename('youth')['name']
        elif self.get_age() >= AGE_SCHOOL:
            return get_membership_type_by_codename('school')['name']
        else:
            return get_membership_type_by_codename('child')['name']

    def focus_type(self):
        if self.is_household_member() and self.get_age() >= AGE_YOUTH:
            return get_membership_type_by_codename('household')['code']
        elif self.get_age() >= AGE_SENIOR:
            return get_membership_type_by_codename('senior')['code']
        elif self.get_age() >= AGE_MAIN:
            return get_membership_type_by_codename('main')['code']
        elif self.get_age() >= AGE_YOUTH:
            return get_membership_type_by_codename('youth')['code']
        elif self.get_age() >= AGE_SCHOOL:
            return get_membership_type_by_codename('school')['code']
        else:
            return get_membership_type_by_codename('child')['code']

    def price(self):
        if self.is_household_member():
            return min(self.price_by_age(), self.enrollment.get_prices().household)
        else:
            return self.price_by_age()

    def price_by_age(self):
        if self.get_age() >= AGE_SENIOR:    return self.enrollment.get_prices().senior
        elif self.get_age() >= AGE_MAIN:    return self.enrollment.get_prices().main
        elif self.get_age() >= AGE_YOUTH:   return self.enrollment.get_prices().youth
        elif self.get_age() >= AGE_SCHOOL:  return self.enrollment.get_prices().school
        else:                               return self.enrollment.get_prices().child

    def focus_receive_yearbook(self):
        if self.is_household_member():
            return False

        if self.get_age() < AGE_YOUTH:
            return False

        return True

    def save_to_focus(self, linked_to=None):
        first_name, last_name = self.name.rsplit(' ', 1)
        total_price = self.price()
        linked_to = '' if linked_to is None else str(linked_to)

        # Yearbook
        if self.enrollment.country == 'NO':
            # Override yearbook value for norwegians based on age and household status
            receive_yearbook = self.focus_receive_yearbook()
        else:
            # Foreigners need to pay shipment price for the yearbook, so if they match the
            # criteria to receive it, let them choose whether or not to get it
            receive_yearbook = self.can_have_yearbook() and self.enrollment.wants_yearbook
            if receive_yearbook:
                total_price += FOREIGN_SHIPMENT_PRICE
        if receive_yearbook:
            yearbook_type = 152
        else:
            yearbook_type = ''

        # Address
        adr1 = self.enrollment.address1
        if self.enrollment.country == 'NO':
            adr2 = ''
            adr3 = ''
            zipcode = self.enrollment.zipcode
            area = self.enrollment.area
        elif self.enrollment.country == 'DK' or self.enrollment.country == 'SE':
            adr2 = ''
            adr3 = "%s-%s %s" % (self.enrollment.country, self.enrollment.zipcode, self.enrollment.area)
            zipcode = '0000'
            area = ''
        else:
            adr2 = self.enrollment.address2
            adr3 = self.enrollment.address3
            zipcode = '0000'
            area = ''

        # Fetch and increment memberid with stored procedure
        with transaction.commit_manually():
            cursor = connections['focus'].cursor()
            cursor.execute("exec sp_custTurist_updateMemberId")
            memberid = cursor.fetchone()[0]
            connections['focus'].commit_unless_managed()

        focus_user = FocusEnrollment(
            memberid=memberid,
            last_name=last_name,
            first_name=first_name,
            birth_date=self.dob,
            gender='M' if self.gender == 'm' else 'K',
            linked_to=linked_to,
            adr1=adr1,
            adr2=adr2,
            adr3=adr3,
            country_code=self.enrollment.country,
            phone_home='',
            email=self.email,
            receive_yearbook=receive_yearbook,
            type=self.focus_type(),
            yearbook=yearbook_type,
            payment_method=PAYMENT_METHOD_CODES[self.enrollment.payment_method],
            phone_mobile=self.phone,
            zipcode=zipcode,
            area=area,
            language='nb_no',
            totalprice=total_price
        )
        focus_user.save()

        self.memberid = memberid
        self.save()

class Transaction(models.Model):
    enrollment = models.ForeignKey(Enrollment, related_name='transactions')
    transaction_id = models.CharField(max_length=32)
    order_number = models.CharField(max_length=32)

    # active=True for the active transaction of a set of transactions - where state='register' -
    # in an enrollment. Only one transaction in such a set should be True at any time
    active = models.BooleanField(default=False)

    STATE_CHOICES = (
        ('register', 'Startet, men ikke gjennomført'),
        ('cancel', 'Avbrutt av kunden'),
        ('fail', 'Avslått av banken'),
        ('success', 'Betaling godkjent'),
    )
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default=STATE_CHOICES[0][0])
    initiated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_state(self):
        return [c[1] for c in self.STATE_CHOICES if c[0] == self.state][0]

    @staticmethod
    def generate_order_number():
        order_number = random.randint(100000000, 999999999)
        while Transaction.objects.filter(order_number=order_number).exists():
            order_number = random.randint(100000000, 999999999)
        # The I_ convension is there for historical reasons, and memberservice is using
        # it to filter the different payment types when validating all sums.
        # E.g. F_ is used for foreign payments
        return 'I_%s' % order_number

    class Meta:
        ordering = ['-initiated']
