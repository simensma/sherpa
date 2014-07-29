# encoding: utf-8
from datetime import datetime, date
import logging

from django.db import models
from django.core.cache import cache
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from focus.util import get_membership_type_by_code, get_membership_type_by_codename, FJELLOGVIDDE_SERVICE_CODE, YEARBOOK_SERVICE_CODES, FOREIGN_POSTAGE_SERVICE_CODES, PAYMENT_METHOD_CODES, HOUSEHOLD_MEMBER_SERVICE_CODES, MEMBERSHIP_TYPES

logger = logging.getLogger('sherpa')

class Enrollment(models.Model):
    tempid = models.FloatField(db_column=u'tempID', null=True, default=None)
    memberid = models.IntegerField(db_column=u'memberID', primary_key=True)
    first_name = models.CharField(db_column=u'Firstname', max_length=255)
    last_name = models.CharField(db_column=u'Lastname', max_length=255)
    birth_date = models.DateTimeField(db_column=u'Birthdate')
    gender = models.CharField(db_column=u'Gender', max_length=1, choices=(('M', 'Mann'), ('K', 'Kvinne')))
    phone_home = models.CharField(db_column=u'Phone', max_length=255)
    phone_mobile = models.CharField(db_column=u'Mob', max_length=255)
    email = models.TextField(db_column=u'Email')

    adr1 = models.CharField(db_column=u'Adr1', max_length=255)
    adr2 = models.CharField(db_column=u'Adr2', max_length=255)
    adr3 = models.CharField(db_column=u'Adr3', max_length=255)
    zipcode = models.CharField(db_column=u'Postnr', max_length=255)
    area = models.CharField(db_column=u'Poststed', max_length=255)
    country_code = models.CharField(max_length=255, db_column=u'Country')

    payment_method = models.IntegerField(db_column=u'Paymethod')
    paid = models.BooleanField(db_column=u'Payed', default=False)
    totalprice = models.FloatField(db_column=u'TotalPrice')

    registration_date = models.DateTimeField(db_column=u'Regdate', auto_now_add=True)

    linked_to = models.CharField(db_column=u'LinkedTo', max_length=255)
    enlisted_by = models.CharField(db_column=u'EnlistedBy', max_length=255, default=0)
    enlisted_article = models.CharField(db_column=u'EnlistedArticle', max_length=255, default=None)
    receive_yearbook = models.BooleanField(db_column=u'ReceiveYearbook')
    type = models.FloatField(db_column=u'Type')
    yearbook = models.CharField(db_column=u'Yearbook', max_length=255)
    contract_giro = models.BooleanField(db_column=u'ContractGiro', default=False)
    language = models.CharField(max_length=255)
    receive_email = models.BooleanField(db_column=u'ReceiveEmail', default=True)
    receive_sms = models.BooleanField(db_column=u'ReceiveSms', default=True)
    submitted_by = models.CharField(db_column=u'SubmittedBy', max_length=255, null=True, default=None)
    submitted_date = models.DateTimeField(db_column=u'SubmittedDt', null=True, default=None)
    updated_card = models.BooleanField(db_column=u'UpdatedCard', default=False)

    def __unicode__(self):
        return u'%s (memberid: %s)' % (self.pk, self.memberid)

    def has_paid(self):
        return self.payment_method == PAYMENT_METHOD_CODES['card'] and self.paid == True

    @staticmethod
    def get_active():
        return Enrollment.objects.filter(
            Q(payment_method=PAYMENT_METHOD_CODES['card']) |
            Q(payment_method=PAYMENT_METHOD_CODES['invoice']),
            submitted_date__isnull=True
        )

    class Meta:
        db_table = u'CustTurist_members'

class Actor(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'SeqNo')

    # User data
    first_name = models.CharField(max_length=50, db_column=u'FiNm')
    last_name = models.CharField(max_length=50, db_column=u'Nm')
    birth_date = models.DateTimeField(null=True, db_column=u'BDt')
    gender = models.CharField(max_length=1, db_column=u'Sex')
    email = models.CharField(max_length=250, db_column=u'EMail')
    phone_home = models.CharField(max_length=50, db_column=u'Ph')
    phone_mobile = models.CharField(max_length=50, db_column=u'MobPh')

    # Membership information
    memberid = models.IntegerField(unique=True, db_column=u'ActNo')
    parent = models.IntegerField(db_column=u'ActRel6')
    main_forening_id = models.IntegerField(db_column=u'ActRel4')
    local_forening_id = models.IntegerField(db_column=u'ActRel5')

    # Enrollment/resignation date and reason
    start_date = models.DateTimeField(null=True, db_column=u'StartDt')
    start_code = models.CharField(max_length=5, db_column=u'StartCd')
    end_date = models.DateTimeField(null=True, db_column=u'EndDt')
    end_code = models.CharField(max_length=5, db_column=u'EndCd')

    # Other relevant stuff
    receive_email = models.BooleanField(db_column=u'OptBit1')
    reserved_against_partneroffers = models.BooleanField(db_column=u'OptBit3')

    orgno = models.CharField(max_length=50, db_column=u'OrgNo')
    fax = models.CharField(max_length=50, db_column=u'Fax')
    web = models.CharField(max_length=250, db_column=u'Web')
    pno = models.CharField(max_length=50, db_column=u'PNo')
    type = models.CharField(max_length=50, db_column=u'Type')
    adtype = models.CharField(max_length=3, db_column=u'AdType')
    note1 = models.TextField(db_column=u'Note1')
    note2 = models.TextField(db_column=u'Note2')
    payterm = models.IntegerField(db_column=u'PayTerm')
    accno = models.CharField(max_length=50, db_column=u'AccNo')
    disc = models.SmallIntegerField(null=True, db_column=u'Disc')
    vatcd = models.BooleanField(db_column=u'VatCd')
    optint1 = models.IntegerField(db_column=u'OptInt1')
    optint2 = models.IntegerField(db_column=u'OptInt2')
    optint3 = models.IntegerField(db_column=u'OptInt3')
    optint4 = models.IntegerField(db_column=u'OptInt4')
    optint5 = models.IntegerField(db_column=u'OptInt5')
    optint6 = models.IntegerField(db_column=u'OptInt6')
    optint7 = models.IntegerField(db_column=u'OptInt7')
    optint8 = models.IntegerField(db_column=u'OptInt8')
    optint9 = models.IntegerField(db_column=u'OptInt9')
    optchar1 = models.CharField(max_length=10, db_column=u'OptChar1')
    optchar2 = models.CharField(max_length=10, db_column=u'OptChar2')
    optchar3 = models.CharField(max_length=10, db_column=u'OptChar3')
    optchar4 = models.CharField(max_length=10, db_column=u'OptChar4')
    optchar5 = models.CharField(max_length=10, db_column=u'OptChar5')
    optchar6 = models.CharField(max_length=10, db_column=u'OptChar6')
    optchar7 = models.CharField(max_length=10, db_column=u'OptChar7')
    optchar8 = models.CharField(max_length=10, db_column=u'OptChar8')
    optchar9 = models.CharField(max_length=10, db_column=u'OptChar9')
    optbit2 = models.BooleanField(db_column=u'OptBit2')
    optbit4 = models.BooleanField(db_column=u'OptBit4')
    optbit5 = models.BooleanField(db_column=u'OptBit5')
    optbit6 = models.BooleanField(db_column=u'OptBit6')
    optlng1 = models.FloatField(db_column=u'OptLng1')
    optlng2 = models.FloatField(db_column=u'OptLng2')
    optlng3 = models.FloatField(db_column=u'OptLng3')
    optdate1 = models.DateTimeField(null=True, db_column=u'OptDate1')
    optdate2 = models.DateTimeField(null=True, db_column=u'OptDate2')
    optdate3 = models.DateTimeField(null=True, db_column=u'OptDate3')
    optdate4 = models.DateTimeField(null=True, db_column=u'OptDate4')
    county1 = models.CharField(max_length=50, db_column=u'County1')
    county2 = models.CharField(max_length=50, db_column=u'County2')
    actrel1 = models.IntegerField(db_column=u'ActRel1')
    actrel2 = models.IntegerField(db_column=u'ActRel2')
    actrel3 = models.IntegerField(db_column=u'ActRel3')
    actrel7 = models.IntegerField(null=True, db_column=u'ActRel7')
    actrel8 = models.IntegerField(null=True, db_column=u'ActRel8')
    actrel9 = models.IntegerField(null=True, db_column=u'ActRel9')
    inf1 = models.CharField(max_length=50, db_column=u'Inf1')
    inf2 = models.CharField(max_length=50, db_column=u'Inf2')
    inf3 = models.CharField(max_length=50, db_column=u'Inf3')
    inf4 = models.CharField(max_length=50, db_column=u'Inf4')
    inf5 = models.CharField(max_length=50, db_column=u'Inf5')
    webusr = models.CharField(max_length=50, db_column=u'WebUsr')
    webpw = models.CharField(max_length=50, db_column=u'WebPw')
    websh = models.IntegerField(db_column=u'WebSh')
    weblang = models.CharField(max_length=5, db_column=u'WebLang')
    webcrby = models.CharField(max_length=25, db_column=u'WebCrBy')
    webcrdt = models.DateTimeField(null=True, db_column=u'WebCrDt')
    crby = models.CharField(max_length=25, db_column=u'CrBy')
    crdt = models.DateTimeField(db_column=u'CrDt')
    chby = models.CharField(max_length=25, db_column=u'ChBy')
    chdt = models.DateTimeField(db_column=u'ChDt')

    def __unicode__(self):
        return u'%s (memberid: %s)' % (self.pk, self.memberid)

    def is_personal_member(self):
        # Note that we're ignoring the stop_date. We just need to know if this is a personal membership or not,
        # we don't care if the type changed or they haven't paid their membership (which is likely why stop_date
        # would be set)
        return self.get_services().filter(
            code__gte=min([t['code'] for t in MEMBERSHIP_TYPES]),
            code__lte=max([t['code'] for t in MEMBERSHIP_TYPES]),
        ).exists()

    def membership_type(self):
        # Supposedly, there should only be one service in the range of membership types.
        try:
            # Try filtering on stop_date; some members have multiple services with only one of them not stopped
            membership_type_service = self.get_services().get(
                Q(stop_date__isnull=True) | Q(stop_date__gt=datetime.now()),
                code__gte=min([t['code'] for t in MEMBERSHIP_TYPES]),
                code__lte=max([t['code'] for t in MEMBERSHIP_TYPES]),
            )
        except ActorService.DoesNotExist:
            # No service with stop_date not set, try ignoring the stop_date; that would be a member who hasn't paid.
            # If there's more than one, we have no way of knowing which service is relevant.
            # If there's no such service, this isn't a personal membership and this method should never have been
            # called for this Actor.
            membership_type_service = self.get_services().get(
                code__gte=min([t['code'] for t in MEMBERSHIP_TYPES]),
                code__lte=max([t['code'] for t in MEMBERSHIP_TYPES]),
            )

        code = int(membership_type_service.code.strip())
        return get_membership_type_by_code(code)

    def has_membership_type(self, codename):
        # Note that you shouldn't use this to check for the 'household' membership type,
        # use is_household_member() -- see the docs on that method for more info.
        return self.membership_type() == get_membership_type_by_codename(codename)

    def get_services(self):
        services = cache.get('actor.services.%s' % self.memberid)
        if services is None:
            services = self.services.all()
            cache.set('actor.services.%s' % self.memberid, services, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return services

    def get_invoice_type(self):
        # Invoice type is stored as a service column with the same value in all rows. What the fuck :)
        return self.get_services()[0].invoicetype

    def get_invoice_type_text(self):
        # Note: The old member system checked for 5, and regarded it as both 'avtalegiro' and 'efaktura'.
        # However, absolutely no records exist with that value, so we'll ignore that here.
        if self.get_invoice_type() == 1:
            return 'avtalegiro'
        elif self.get_invoice_type() == 3:
            return 'efaktura'
        else:
            return ''

    def get_first_name(self):
        if self.first_name is None:
            return ''
        else:
            return self.first_name.strip()

    def get_last_name(self):
        if self.last_name is None:
            return ''
        else:
            return self.last_name.strip()

    def get_full_name(self):
        return ("%s %s" % (self.get_first_name(), self.get_last_name())).strip()

    def get_email(self):
        return self.email.strip() if self.email is not None else ''

    def set_email(self, email):
        self.email = email
        self.save()

    def get_birth_date(self):
        return self.birth_date

    def get_age(self):
        return (datetime.now() - self.get_birth_date()).days / 365

    def get_gender(self):
        if self.gender.lower() == 'm':
            return 'm'
        elif self.gender.lower() == 'k':
            return 'f'
        else:
            return None

    def get_phone_home(self):
        return self.phone_home.strip() if self.phone_home is not None else ''

    def get_phone_mobile(self):
        return self.phone_mobile.strip() if self.phone_mobile is not None else ''

    def get_parent_memberid(self):
        if self.parent == 0 or self.parent == self.memberid:
            return None
        else:
            return self.parent

    def get_children(self):
        children = cache.get('actor.children.%s' % self.memberid)
        if children is None:
            children = Actor.get_personal_members().filter(parent=self.memberid).exclude(id=self.id)
            cache.set('actor.children.%s' % self.memberid, children, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return children

    def is_household_member(self):
        """
        Note that the definition of a household member is vague; membership type codes
        (defined by Focus services) include "household member" but it is only used when
        the member is an adult - if it is a child, a "child member" service is used instead,
        even though they do have a parent (and hence is a household member).

        *Having a separate parent* is the canonical definition of a household member.
        However, there are also a few cases where the membership type is used even though
        there isn't a parent is set, so handle both cases.
        """
        is_household_by_parent = self.parent != 0 and self.parent != self.memberid
        is_household_by_service = self.get_services().filter(code__in=HOUSEHOLD_MEMBER_SERVICE_CODES).exists()
        return is_household_by_parent or is_household_by_service

    def has_paid(self):
        """
        Checks if the membership is *currently* paid.
        """
        from core.util import membership_year_start
        if date.today() >= membership_year_start()['actual_date']:
            return self.has_paid_this_year() or self.has_paid_next_year()
        else:
            return self.has_paid_this_year()

    def has_paid_this_year(self):
        """
        Checks if the membership is paid for the current year. This is how we find out that
        a membership is valid after årskravet/before new years for the remainder of the year.
        """
        from core.util import membership_year_start
        if date.today() >= membership_year_start()['actual_date']:
            return self.has_paid_this_year_after_arskrav()
        else:
            return self.balance_is_paid()

    def has_paid_next_year(self):
        """
        Checks if this member has paid for the next membership year. Can only be called after
        årskravet. A False result doesn't mean they're not a valid member right now.
        """
        from core.util import membership_year_start
        if not date.today() >= membership_year_start()['actual_date']:
            raise Exception("Doesn't make sense to call this method before årskravet")
        return self.balance_is_paid()

    def balance_is_paid(self):
        """
        Checks if the balance view says that the membership is paid. Means different things
        before and after årskravet, you usually want to check has_paid_{this,next}_year instead.
        """
        has_paid = cache.get('actor.balance.%s' % self.memberid)
        if has_paid is None:
            try:
                has_paid = self.balance.is_paid()
            except BalanceHistory.DoesNotExist:
                # Not-existing balance for this year means that they haven't paid
                has_paid = False
            cache.set('actor.balance.%s' % self.memberid, has_paid, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return has_paid

    def has_paid_this_year_after_arskrav(self):
        """
        In the period after årskravet but before year's end, members who have paid for the current
        year (but not the next) should apparently have no end_date (and those who haven't, do).
        """
        from core.util import membership_year_start
        if not date.today() >= membership_year_start()['actual_date']:
            raise Exception("Doesn't make sense to call this method before årskravet")
        return self.end_date is None

    # The members that can recieve publications to their household (but don't necessarliy have the actual
    # service themselves - e.g. household members are eligible but their main member has the service)
    def is_eligible_for_publications(self):
        # Household members are eligible if their parents are eligible
        if self.is_household_member():
            return Actor.get_personal_members().get(memberid=self.get_parent_memberid()).is_eligible_for_publications()

        # This membership type is supposed to be deprecated, but error logs show it's still in use
        if self.has_membership_type("household_without_main"):
            return False

        # Young main members (school/child) won't recieve publications
        if self.has_membership_type("school") or self.has_membership_type("child"):
            return False

        return True

    # The kind of members that are allowed to reserve against receiving publications
    def can_reserve_against_publications(self):
        # Household members don't have the service; their main member does
        if self.is_household_member():
            return False

        # This membership type is supposed to be deprecated, but error logs show it's still in use
        if self.has_membership_type("household_without_main"):
            return False

        # Not sure why lifelong members can't reserve, but memberservice said that they shouldn't
        if self.has_membership_type("lifelong"):
            return False

        # Foreign members can't change it here because it has extra costs associated
        if self.get_clean_address().country.code != 'NO':
            return False

        # Young main members (school/child) won't recieve publications
        if self.has_membership_type("school") or self.has_membership_type("child"):
            return False

        # Everyone else can reserve if they want
        return True

    def get_fjellogvidde_service(self):
        services = self.get_services().filter(code=FJELLOGVIDDE_SERVICE_CODE)
        if len(services) == 0:
            # This assumes that the actor *has* the F&V service, I suspect that assumption
            # will sometimes be incorrect
            raise Exception("Expected at least one Fjell og Vidde-service to exist in Focus")
        elif len(services) == 1:
            return services[0]
        else:
            # If >1 of the same service, regard the one with newest start_date as canonical
            return max(services, key=lambda s: s.start_date)

    def get_yearbook_service(self):
        services = self.get_services().filter(code__in=YEARBOOK_SERVICE_CODES)
        if len(services) == 0:
            # This assumes that the actor *has* the yearbook service, I suspect that assumption
            # will sometimes be incorrect
            raise Exception("Expected at least one Yearbook-service to exist in Focus")
        elif len(services) == 1:
            return services[0]
        else:
            # If >1 of the same service, regard the one with newest start_date as canonical.
            # Note: We're disregarding the fact that there are multiple yearbook service codes.
            # Even though no one is supposed to have that, it's technically possible - assuming
            # that the newest one is canonical *might* be wrong.
            return max(services, key=lambda s: s.start_date)

    def get_reserved_against_fjellogvidde(self):
        return self.get_fjellogvidde_service().stop_date is not None

    def set_reserved_against_fjellogvidde(self, reserved):
        service = self.get_fjellogvidde_service()
        if reserved:
            note = u'Ønsker ikke Fjell og Vidde (aktivert gjennom Min Side).'
        else:
            note = u'Ønsker Fjell og Vidde (aktivert gjennom Min Side).'
        self.set_service_status(service, not reserved, note)
        cache.delete('actor.services.%s' % self.memberid)

    def get_reserved_against_yearbook(self):
        return self.get_yearbook_service().stop_date is not None

    def set_reserved_against_yearbook(self, reserved):
        service = self.get_yearbook_service()
        if reserved:
            note = u'Ønsker ikke tilsendt årbok (aktivert gjennom Min Side).'
        else:
            note = u'Ønsker tilsendt årbok(aktivert gjennom Min Side).'
        self.set_service_status(service, not reserved, note)
        cache.delete('actor.services.%s' % self.memberid)

    def set_service_status(self, service, enable, note=None):
        if enable:
            service.stop_date = None
            service.save()
        else:
            service.stop_date = datetime.now()
            service.save()
        if note is not None:
            text = ActorText(
                actor=self,
                memberid=self.memberid,
                text=note,
                created_by=self.memberid,
                created_date=datetime.now())
            text.save()

    # Publication statuses for foreign members

    def has_foreign_postage(self):
        if self.get_clean_address().country.code == 'NO':
            raise Exception("It doesn't make sense to check for foreign postage on domestic members.")
        try:
            # Note that we're not failing if there are multiple active services even though there should only be one.
            return self.get_services().filter(code__in=FOREIGN_POSTAGE_SERVICE_CODES, stop_date__isnull=True).exists()
        except ActorService.DoesNotExist:
            return False

    def has_foreign_fjellogvidde_service(self):
        if not self.has_foreign_postage():
            return False
        try:
            return self.get_fjellogvidde_service().stop_date is None
        except ActorService.DoesNotExist:
            return False

    # Again assuming that all Actors only have ONE of the yearbook services.
    def has_foreign_yearbook_service(self):
        if not self.has_foreign_postage():
            return False
        try:
            return self.get_yearbook_service().stop_date is None
        except ActorService.DoesNotExist:
            return False

    def get_clean_address(self):
        from focus.abstractions import ActorAddressClean
        return ActorAddressClean(self.address)

    @staticmethod
    def get_personal_members():
        """Returns Actor objects defined as personal members (has a service with one of the membership type codes).
        Other objects may be foreninger, organizations or other non-private member types which we currently
        aren't supporting. Note that this should probably be used for any Actor lookup, but we might have missed
        a few spots."""
        # Note that we're ignoring the stop_date. We just need to know if this is a personal membership or not,
        # we don't care if the type changed or they haven't paid their membership (which is likely why stop_date
        # would be set)
        return Actor.objects.filter(
            services__code__gte=min([t['code'] for t in MEMBERSHIP_TYPES]),
            services__code__lte=max([t['code'] for t in MEMBERSHIP_TYPES]),
        ).distinct()

    @staticmethod
    def all_active_members():
        return Actor.get_personal_members().filter(
            Q(end_date=date(year=2014, month=12, day=31)) |
            Q(end_date__isnull=True),
            # Balance should actually check for 0, but checks 1 because apparently there are some
            # payments where some øre are left (although I personally suspect it to be caused by using
            # the float datatype incorrectly)
            balance__current_year__lte=1,
            services__code__in=[t['code'] for t in MEMBERSHIP_TYPES],
            main_forening_id__in=range(10, 100) # Valid focus-forening ids are in this range
        )

    class Meta:
        db_table = u'Actor'

# This receiver should keep track of all cache keys related to an actor, and delete them.
# So whenever you add a new actor-related key to the cache, remember to delete it here!
# Someone is sure to forget to do that sometime, so please "synchronize" manually sometime.
@receiver(post_save, sender=Actor, dispatch_uid="focus.models")
def delete_actor_cache(sender, **kwargs):
    cache.delete('actor.%s' % kwargs['instance'].memberid)
    cache.delete('actor.services.%s' % kwargs['instance'].memberid)
    cache.delete('actor.children.%s' % kwargs['instance'].memberid)
    cache.delete('actor.balance.%s' % kwargs['instance'].memberid)
    for child in kwargs['instance'].get_children():
        cache.delete('actor.%s' % child.memberid)
        cache.delete('actor.services.%s' % child.memberid)
        cache.delete('actor.balance.%s' % child.memberid)

class ActorService(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'SeqNo')
    actor = models.ForeignKey(Actor, related_name='services', db_column=u'ActSeqNo')
    memberid = models.IntegerField(null=True, db_column=u'ActNo')

    code = models.CharField(max_length=25, db_column=u'ArticleNo')
    start_date = models.DateTimeField(null=True, db_column=u'StartDt')
    end_date = models.DateTimeField(null=True, db_column=u'EndDt')
    stop_date = models.DateTimeField(null=True, db_column=u'StopDt')

    actpayno = models.IntegerField(null=True, db_column=u'ActPayNo')
    invoicetype = models.IntegerField(null=True, db_column=u'InvType')
    invprinttype = models.IntegerField(null=True, db_column=u'InvPrintType')
    newstartdt = models.DateTimeField(null=True, db_column=u'NewStartDt')
    previousinvoicedt = models.DateTimeField(null=True, db_column=u'PreviousInvoiceDt')
    invoicefreq = models.IntegerField(null=True, db_column=u'InvoiceFreq')
    pricecd = models.IntegerField(null=True, db_column=u'PriceCd')
    price = models.FloatField(null=True, db_column=u'Price')
    qty = models.FloatField(null=True, db_column=u'Qty')
    optint1 = models.IntegerField(null=True, db_column=u'OptInt1')
    description = models.TextField(db_column=u'Description')
    crby = models.CharField(max_length=25, db_column=u'CrBy')
    crdt = models.DateTimeField(null=True, db_column=u'CrDt')
    chby = models.CharField(max_length=25, db_column=u'ChBy')
    chdt = models.DateTimeField(null=True, db_column=u'ChDt')
    invdate = models.DateTimeField(null=True, db_column=u'InvDate')

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'ActService'

class ActorAddress(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'SeqNo')
    actor = models.OneToOneField(Actor, unique=True, related_name='address', db_column=u'ActSeqNo')
    actnojoin = models.IntegerField(db_column=u'ActNoJoin')
    actadtype = models.CharField(max_length=3, unique=True, db_column=u'ActAdType')
    a1 = models.CharField(max_length=40, db_column=u'A1')
    a2 = models.CharField(max_length=40, db_column=u'A2')
    a3 = models.CharField(max_length=40, db_column=u'A3')
    zipcode = models.CharField(max_length=9, db_column=u'PCode')
    area = models.CharField(max_length=30, db_column=u'PArea')
    country_code = models.CharField(max_length=3, db_column=u'CtryCode')
    frdt = models.DateTimeField(null=True, db_column=u'FrDt')
    todt = models.DateTimeField(null=True, db_column=u'ToDt')
    chby = models.CharField(max_length=50, db_column=u'ChBy')
    chdt = models.DateTimeField(null=True, db_column=u'ChDt')
    crby = models.CharField(max_length=50, db_column=u'CrBy')
    crdt = models.DateTimeField(null=True, db_column=u'CrDt')

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'ActAd'

class ActorText(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'SeqNo')
    actor = models.ForeignKey(Actor, unique=True, related_name='text', db_column=u'ActSeqNo')
    memberid = models.IntegerField(null=True, db_column=u'ActNo')

    type = models.CharField(max_length=50, db_column=u'TxtType')
    name = models.CharField(max_length=50, db_column=u'TxtNm')
    text = models.TextField(db_column=u'Description')

    created_by = models.CharField(max_length=25, db_column=u'CrBy')
    created_date = models.DateTimeField(null=True, db_column=u'CrDt')
    changed_by = models.CharField(max_length=25, db_column=u'ChBy')
    changed_date = models.DateTimeField(null=True, db_column=u'ChDt')

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'ActText'

# The Zipcode table connects zipcodes to counties and foreninger.
class FocusZipcode(models.Model):

    # Zipcode + Area
    zipcode = models.CharField(max_length=9, primary_key=True, db_column=u'PostCode')
    area = models.CharField(max_length=40, db_column=u'PostArea')

    # City code/name
    city_code = models.CharField(max_length=10, db_column=u'County2No')
    city_name = models.CharField(max_length=40, db_column=u'County2Name')

    # The county code, actually corresponding to ISO 3166-2:NO (https://no.wikipedia.org/wiki/ISO_3166-2:NO)
    # Plus the code '99' which in Focus means international
    county_code = models.CharField(max_length=10, db_column=u'County1No')
    county_name = models.CharField(max_length=40, db_column=u'County1Name')

    # Conncetions to foreninger.
    # The main id corresponds to the 'focus_id' field in the Forening model.
    # The local id is in practice not (yet) used/connected to their foreninger.
    main_forening_id = models.IntegerField(null=True, db_column=u'District1')
    local_forening_id = models.IntegerField(null=True, db_column=u'District2')

    # Other stuff
    crby = models.CharField(max_length=25, db_column=u'CrBy')
    crdt = models.DateTimeField(null=True, db_column=u'CrDt')
    chby = models.CharField(max_length=25, db_column=u'ChBy')
    chdt = models.DateTimeField(null=True, db_column=u'ChDt')

    def __unicode__(self):
        return u'%s (zipcode: %s)' % (self.pk, self.zipcode)

    class Meta:
        db_table = u'PostalCode'

class Price(models.Model):
    forening_id = models.IntegerField(primary_key=True, db_column=u'Region')
    main = models.IntegerField(null=True, db_column=u'C101')
    youth = models.IntegerField(null=True, db_column=u'C102')
    senior = models.IntegerField(null=True, db_column=u'C103')
    lifelong = models.IntegerField(null=True, db_column=u'C104')
    child = models.IntegerField(null=True, db_column=u'C105')
    school = models.IntegerField(null=True, db_column=u'C106')
    household = models.IntegerField(null=True, db_column=u'C107')
    unknown = models.IntegerField(null=True, db_column=u'C108')

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'Cust_Turist_Region_PriceCode_CrossTable'

class BalanceHistory(models.Model):
    """
    This is a view which uses 2-3 other views/tables to collect some sort of balance.
    Instead of wasting time studying its logic, we'll just use this view to get the
    data we need, even though it performs relatively slow.
    """

    id = models.OneToOneField(Actor, related_name='balance', primary_key=True, db_column=u'ActSeqNo')
    memberid = models.IntegerField(db_column=u'ActActNo')
    current_year = models.FloatField(db_column=u'ThisYear') # Dammit, this returns float, smells like trouble
    # Note - this view also has a 'LastYear' column. That field retrieves info from the table
    # "Cust_Turist_Balance_Hist", but upon further inspection, that table has no entry for member with
    # memberid above 3000000 - which is from ca 2006. This probably means that it is not in use anymore,
    # so we'll ignore it. It was used in the old user page - after årskravet is processed, a members
    # payment status would be if _either_ the current_year or last_year balance was <= 0.

    def __unicode__(self):
        return u'%s' % self.pk

    def is_paid(self):
        """
        Note that after in the period after the årskrav has been processed but before the actual year
        has ended, this will be checking if they have paid for the *NEXT* year. It does NOT account
        for existing members who paid for the current year, but not the next - however they should still
        have access to member services - that'll have to be checked by the caller as well.
        """
        # Focus uses the float datatype, and we've for example encountered one member with
        # NOK 2.7283730830163222e-14 outstanding. That's why we're checking below 0.001 and not 0.
        return self.current_year <= 0.001

    class Meta:
        db_table = u'Cust_Turist_Balance_Hist_v'
