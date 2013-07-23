# encoding: utf-8
from django.db import models
from django.core.cache import cache
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from datetime import datetime
import logging
import sys

from association.models import Association
from sherpa2.models import Association as Sherpa2Association
from core.models import County, FocusCountry, Zipcode
from focus.util import get_membership_type_by_code, get_membership_type_by_codename, FJELLOGVIDDE_SERVICE_CODE, YEARBOOK_SERVICE_CODES, FOREIGN_POSTAGE_SERVICE_CODE

logger = logging.getLogger('sherpa')

class Enrollment(models.Model):
    tempid = models.FloatField(db_column=u'tempID', null=True, default=None)
    member_id = models.IntegerField(db_column=u'memberID', primary_key=True)
    last_name = models.CharField(db_column=u'Lastname', max_length=255)
    first_name = models.CharField(db_column=u'Firstname', max_length=255)
    dob = models.DateTimeField(db_column=u'Birthdate')
    gender = models.CharField(db_column=u'Gender', max_length=1, choices=(('M', 'Mann'), ('K', 'Kvinne')))
    linked_to = models.CharField(db_column=u'LinkedTo', max_length=255)
    enlisted_by = models.CharField(db_column=u'EnlistedBy', max_length=255, default=0)
    enlisted_article = models.CharField(db_column=u'EnlistedArticle', max_length=255, default=None)
    adr1 = models.CharField(db_column=u'Adr1', max_length=255)
    adr2 = models.CharField(db_column=u'Adr2', max_length=255)
    adr3 = models.CharField(db_column=u'Adr3', max_length=255)
    country = models.CharField(max_length=255, db_column=u'Country')
    phone = models.CharField(db_column=u'Phone', max_length=255)
    email = models.TextField(db_column=u'Email')
    receive_yearbook = models.BooleanField(db_column=u'ReceiveYearbook')
    type = models.FloatField(db_column=u'Type')
    yearbook = models.CharField(db_column=u'Yearbook', max_length=255)
    payment_method = models.FloatField(db_column=u'Paymethod')
    contract_giro = models.BooleanField(db_column=u'ContractGiro', default=False)
    mob = models.CharField(db_column=u'Mob', max_length=255)
    postnr = models.CharField(db_column=u'Postnr', max_length=255)
    poststed = models.CharField(db_column=u'Poststed', max_length=255)
    language = models.CharField(max_length=255)
    totalprice = models.FloatField(db_column=u'TotalPrice')
    paid = models.BooleanField(db_column=u'Payed', default=False)
    reg_date = models.DateTimeField(db_column=u'Regdate', auto_now_add=True)
    receive_email = models.BooleanField(db_column=u'ReceiveEmail', default=True)
    receive_sms = models.BooleanField(db_column=u'ReceiveSms', default=True)
    submitted_by = models.CharField(db_column=u'SubmittedBy', max_length=255, null=True, default=None)
    submitted_date = models.DateTimeField(db_column=u'SubmittedDt', null=True, default=None)
    updated_card = models.BooleanField(db_column=u'UpdatedCard', default=False)

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
    main_association_id = models.IntegerField(db_column=u'ActRel4')
    local_association_id = models.IntegerField(db_column=u'ActRel5')

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

    def main_association(self):
        association = cache.get('focus.association.%s' % self.main_association_id)
        if association is None:
            association = Association.objects.get(focus_id=self.main_association_id)
            cache.set('focus.association.%s' % self.main_association_id, association, 60 * 60 * 24 * 7)
        return association

    def main_association_old(self):
        # This sad method returns the association object from the old sherpa2 model.
        # For now it's mostly used to get the site url because most of the new objects
        # don't have an assigned site.
        association = cache.get('focus.association_sherpa2.%s' % self.main_association_id)
        if association is None:
            association = Sherpa2Association.objects.get(focus_id=self.main_association_id)
            cache.set('focus.association_sherpa2.%s' % self.main_association_id, association, 60 * 60 * 24 * 7)
        return association

    def membership_type(self):
        now = datetime.now()
        # Supposedly, there should only be one service in this range
        code = int(self.get_services().get(Q(stop_date__isnull=True) | Q(stop_date__gt=now), code__gt=100, code__lt=110).code.strip())
        return get_membership_type_by_code(code)

    def has_membership_type(self, codename):
        # Note that you shouldn't use this to check for the 'household' membership type,
        # use is_household_member() -- se the docs on that method for more info.
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

    def get_full_name(self):
        return ("%s %s" % (self.first_name, self.last_name)).strip()

    def get_age(self):
        return (datetime.now() - self.birth_date).days / 365

    def get_gender(self):
        if self.gender.lower() == 'm':
            return 'm'
        elif self.gender.lower() == 'k':
            return 'f'
        else:
            return None

    def get_parent(self):
        parent = self.parent
        if not self.is_household_member():
            return None
        if parent == 0 or parent == self.memberid:
            return None
        else:
            actor = cache.get('actor.%s' % self.parent)
            if actor is None:
                actor = Actor.objects.get(memberid=self.parent)
                cache.set('actor.%s' % self.parent, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)
            return actor

    def get_children(self):
        children = cache.get('actor.children.%s' % self.memberid)
        if children is None:
            children = Actor.objects.filter(parent=self.memberid).exclude(id=self.id)
            cache.set('actor.children.%s' % self.memberid, children, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return children

    def is_household_member(self):
        # Note that the definition of a household member is vague; membership type codes
        # (defined by Focus services) include "household member" but it is only used when
        # the member is an adult - if it is a child, a "child member" service is used instead,
        # even though they do have a parent (and hence is a household member).
        # This method defines *having a separate parent* as being a household member and should
        # be considered canonical.
        return self.parent != 0 and self.parent != self.memberid

    def has_paid(self):
        has_paid = cache.get('actor.has_paid.%s' % self.memberid)
        if has_paid is None:
            try:
                has_paid = self.balance.is_paid()
            except BalanceHistory.DoesNotExist:
                # Not-existing balance for this year means that they haven't paid
                has_paid = False
            cache.set('actor.has_paid.%s' % self.memberid, has_paid, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return has_paid

    # The members that can recieve publications to their household (but don't necessarliy have the actual
    # service themselves - e.g. household members are eligible but their main member has the service)
    def is_eligible_for_publications(self):
        # Household members are eligible if their parents are eligible
        if self.is_household_member():
            return self.get_parent().is_eligible_for_publications()

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
            # that the newest one is canonical is likely wrong.
            logger.warning(u"Kom borti et medlem med mer enn én Årbok-tjeneste, antar at den nyeste gjelder",
                exc_info=sys.exc_info(),
                extra={
                    'memberid': self.memberid,
                    'yearbook_service_ids': [s.id for s in services]
                }
            )
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

    def get_reserved_against_yearbook(self):
        return self.get_yearbook_service().stop_date is not None

    def set_reserved_against_yearbook(self, reserved):
        service = self.get_yearbook_service()
        if reserved:
            note = u'Ønsker ikke tilsendt årbok (aktivert gjennom Min Side).'
        else:
            note = u'Ønsker tilsendt årbok(aktivert gjennom Min Side).'
        self.set_service_status(service, not reserved, note)

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
            return self.get_services().get(code=FOREIGN_POSTAGE_SERVICE_CODE).stop_date is None
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
        return ActorAddressClean(self.address)

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
    cache.delete('actor.has_paid.%s' % kwargs['instance'].memberid)
    for child in kwargs['instance'].get_children():
        cache.delete('actor.%s' % child.memberid)
        cache.delete('actor.services.%s' % child.memberid)
        cache.delete('actor.has_paid.%s' % child.memberid)

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

    class Meta:
        db_table = u'ActAd'

# This is NOT a db table, but a cleaner address model, based on Focus' ActorAddress model.
# It has three address fields (field{1,3}), a 'country' field ('core.models.FocusCountry').
# If the country is Norway, it also has a 'zipcode' field ('core.models.Zipcode') and a
# 'county' field ('core.models.County').
# The class has utility methods for typical formatting of addresses (with newlines, and for
# one line with commas).
class ActorAddressClean:
    def __init__(self, address):
        # Add fields, replacing NULL values with the empty string
        self.field1 = address.a1.strip() if address.a1 is not None else ''
        self.field2 = address.a2.strip() if address.a2 is not None else ''
        self.field3 = address.a3.strip() if address.a3 is not None else ''

        # Set the actual country object
        # Uppercase the country code (just in case - you never know with Focus)
        self.country = FocusCountry.objects.get(code=address.country_code.upper())

        if self.country.code == 'NO':
            # Norwegians - set the actual zipcode object
            try:
                self.zipcode = Zipcode.objects.get(zipcode=address.zipcode)
            except Zipcode.DoesNotExist:
                # Some addresses have NULL in the zipcode field for some reason.
                # Use a zipcode object with empty fields.
                self.zipcode = Zipcode()

            # Set the actual County object based on the zipcode
            if self.zipcode.zipcode != '':
                county_code = FocusZipcode.objects.get(zipcode=self.zipcode.zipcode).county_code
                if county_code == '99':
                    # International addresses have county code 99 in Focus. Define the county as None for now.
                    self.county = None
                else:
                    self.county = County.objects.get(code=county_code)
            else:
                self.county = None

        else:
            # Foreigners - ignore zipcode/area
            # Remove country code prefixes
            if self.field1.lower().startswith("%s-" % self.country.code.lower()):
                self.field1 = self.field1[len(self.country.code) + 1:].strip()
            if self.field2.lower().startswith("%s-" % self.country.code.lower()):
                self.field2 = self.field2[len(self.country.code) + 1:].strip()
            if self.field3.lower().startswith("%s-" % self.country.code.lower()):
                self.field3 = self.field3[len(self.country.code) + 1:].strip()

    # This is adapted for user page account details right now - if norwegian,
    # this doesn't display country, if foreigner, it does. If rewritten, account
    # for that and add parameters or something for that usage.
    def format_with_newlines(self):
        if self.country.code == 'NO':
            address_string = self.field1
            if self.field2 != '':
                address_string += '\n%s' % self.field2
            if self.field3 != '':
                address_string += '\n%s' % self.field3
            address_string += '\n%s %s' % (self.zipcode.zipcode, self.zipcode.area.title())
        else:
            address_string = ''
            if self.field1 != '':
                address_string += '%s\n' % self.field1
            if self.field2 != '':
                address_string += '%s\n' % self.field2
            if self.field3 != '':
                address_string += '%s\n' % self.field3
            address_string += "%s, %s" % (self.country.name, self.country.code)
        return address_string

    # This is adapted for NOR-WAY bus tickets emails right now. If rewritten,
    # account for that and add parameters or something for that usage.
    def format_for_oneline(self):
        address_string = self.field1
        if self.field2 != '':
            address_string += ', %s' % self.field2
        if self.field3 != '':
            address_string += ', %s' % self.field3

        if self.country.code == 'NO':
            address_string += ', %s %s' % (self.zipcode.zipcode, self.zipcode.area.title())
        else:
            address_string += ' (%s, %s)' % (self.country.name, self.country.code)
        return address_string

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

    class Meta:
        db_table = u'ActText'

# The Zipcode table connects zipcodes to counties and associations.
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

    # Conncetions to associations.
    # The main id corresponds to the 'focus_id' field in the Association model.
    # The local id is in practice not (yet) used/connected to their associations.
    main_association_id = models.IntegerField(null=True, db_column=u'District1')
    local_association_id = models.IntegerField(null=True, db_column=u'District2')

    # Other stuff
    crby = models.CharField(max_length=25, db_column=u'CrBy')
    crdt = models.DateTimeField(null=True, db_column=u'CrDt')
    chby = models.CharField(max_length=25, db_column=u'ChBy')
    chdt = models.DateTimeField(null=True, db_column=u'ChDt')

    class Meta:
        db_table = u'PostalCode'

class Price(models.Model):
    association_id = models.IntegerField(primary_key=True, db_column=u'Region')
    main = models.IntegerField(null=True, db_column=u'C101')
    youth = models.IntegerField(null=True, db_column=u'C102')
    senior = models.IntegerField(null=True, db_column=u'C103')
    lifelong = models.IntegerField(null=True, db_column=u'C104')
    child = models.IntegerField(null=True, db_column=u'C105')
    school = models.IntegerField(null=True, db_column=u'C106')
    household = models.IntegerField(null=True, db_column=u'C107')
    unknown = models.IntegerField(null=True, db_column=u'C108')

    class Meta:
        db_table = u'Cust_Turist_Region_PriceCode_CrossTable'

# This is a view which uses 2-3 other views/tables to collect some sort of balance.
# Instead of wasting time studying its logic, we'll just use this view to get the
# data we need, even though it performs relatively slow.
class BalanceHistory(models.Model):
    id = models.OneToOneField(Actor, related_name='balance', primary_key=True, db_column=u'ActSeqNo')
    memberid = models.IntegerField(db_column=u'ActActNo')
    current_year = models.FloatField(db_column=u'ThisYear') # Dammit, this returns float, smells like trouble
    # Note - this view also has a 'LastYear' column. That field retrieves info from the table
    # "Cust_Turist_Balance_Hist", but upon further inspection, that table has no entry for member with memberid
    # above 3000000 - which is from ca 2006. This probably means that it is not in use anymore, so we'll ignore it.
    # It was used in the old user page - after October, when "årskrav" is processed, a members payment status
    # Would be if _either_ the current_year or last_year balance was <= 0.

    def is_paid(self):
        # This will be incorrect in the period between "årskrav" processing and year end,
        # but only for those who haven't paid for the *next* year.
        # The user might have paid for the current year, and the membership is valid for the
        # remainder of the year, but Focus treats this 'current year'-field as the next year.
        # So it will be correct for those who have paid for next year.
        # Note that since Focus treats it this way, so do we in our code, based on the current
        # date compared to the current month in settings.MEMBERSHIP_YEAR_START.
        # This means that we DON'T KNOW what the membership status for the current year is
        # after the "årskrav" month, and can't inform about it, e.g. on the account page.
        # This should be fixed. If it is, refactor all usages of this method and rephrase
        # the info presented to the user.
        return self.current_year <= 0

    class Meta:
        db_table = u'Cust_Turist_Balance_Hist_v'
