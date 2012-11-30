# encoding: utf-8
from django.db import models
from django.core.cache import cache

from association.models import Association

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
    payed = models.BooleanField(db_column=u'Payed', default=False)
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
    type = models.CharField(max_length=50, db_column=u'Type')
    memberid = models.IntegerField(db_column=u'ActNo')
    last_name = models.CharField(max_length=50, db_column=u'Nm')
    first_name = models.CharField(max_length=50, db_column=u'FiNm')
    birth_date = models.DateTimeField(null=True, db_column=u'BDt')
    pno = models.CharField(max_length=50, db_column=u'PNo')
    sex = models.CharField(max_length=1, db_column=u'Sex')
    orgno = models.CharField(max_length=50, db_column=u'OrgNo')
    ph = models.CharField(max_length=50, db_column=u'Ph')
    fax = models.CharField(max_length=50, db_column=u'Fax')
    mobph = models.CharField(max_length=50, db_column=u'MobPh')
    email = models.CharField(max_length=250, db_column=u'EMail')
    web = models.CharField(max_length=250, db_column=u'Web')
    adtype = models.CharField(max_length=3, db_column=u'AdType')
    note1 = models.TextField(db_column=u'Note1')
    note2 = models.TextField(db_column=u'Note2')
    startdt = models.DateTimeField(null=True, db_column=u'StartDt')
    startcd = models.CharField(max_length=5, db_column=u'StartCd')
    enddt = models.DateTimeField(null=True, db_column=u'EndDt')
    endcd = models.CharField(max_length=5, db_column=u'EndCd')
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
    optbit1 = models.BooleanField(db_column=u'OptBit1')
    optbit2 = models.BooleanField(db_column=u'OptBit2')
    optbit3 = models.BooleanField(db_column=u'OptBit3')
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
    main_association_id = models.IntegerField(db_column=u'ActRel4')
    local_association_id = models.IntegerField(db_column=u'ActRel5')
    actrel6 = models.IntegerField(null=True, db_column=u'ActRel6')
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

    def membership_type(self):
        # Supposedly, there should only be one service in this range
        return self.membership_type_name(self.services().get(code__gt=100, code__lt=110).code.strip())

    def services(self):
        services = cache.get('actor.services.%s' % self.memberid)
        if services is None:
            services = ActorService.objects.filter(memberid=self.memberid)
            cache.set('actor.services.%s' % self.memberid, 60 * 60)
        return services

    def membership_type_name(self, code):
        # Should be moved to some kind of "Focus utility" module and merged with the
        # functionality currently found in enrollment/views
        if   code == u'101': return u'Hovedmedlem'
        elif code == u'102': return u'Ungdomsmedlem'
        elif code == u'103': return u'Honnørmedlem'
        elif code == u'104': return u'Livsvarig medlem'
        elif code == u'105': return u'Barnemedlem'
        elif code == u'106': return u'Skoleungdomsmedlem'
        elif code == u'107': return u'Husstandsmedlem'
        elif code == u'108': return u'Husstandsmedlem'
        elif code == u'109': return u'Livsvarig husstandsmedlem'

    class Meta:
        db_table = u'Actor'

class ActorService(models.Model):
    id = models.AutoField(primary_key=True, db_column=u'SeqNo')
    actor_id = models.IntegerField(null=True, db_column=u'ActSeqNo')
    memberid = models.IntegerField(null=True, db_column=u'ActNo')
    code = models.CharField(max_length=25, db_column=u'ArticleNo')
    actpayno = models.IntegerField(null=True, db_column=u'ActPayNo')
    invtype = models.IntegerField(null=True, db_column=u'InvType')
    invprinttype = models.IntegerField(null=True, db_column=u'InvPrintType')
    startdt = models.DateTimeField(null=True, db_column=u'StartDt')
    enddt = models.DateTimeField(null=True, db_column=u'EndDt')
    stopdt = models.DateTimeField(null=True, db_column=u'StopDt')
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
    parea = models.CharField(max_length=30, db_column=u'PArea')
    country = models.CharField(max_length=3, db_column=u'CtryCode')
    frdt = models.DateTimeField(null=True, db_column=u'FrDt')
    todt = models.DateTimeField(null=True, db_column=u'ToDt')
    chby = models.CharField(max_length=50, db_column=u'ChBy')
    chdt = models.DateTimeField(null=True, db_column=u'ChDt')
    crby = models.CharField(max_length=50, db_column=u'CrBy')
    crdt = models.DateTimeField(null=True, db_column=u'CrDt')
    class Meta:
        db_table = u'ActAd'

class FocusZipcode(models.Model):
    zipcode = models.CharField(max_length=9, primary_key=True, db_column=u'PostCode')
    postarea = models.CharField(max_length=40, db_column=u'PostArea')
    county1no = models.CharField(max_length=10, db_column=u'County1No')
    county1name = models.CharField(max_length=40, db_column=u'County1Name')
    county2no = models.CharField(max_length=10, db_column=u'County2No')
    county2name = models.CharField(max_length=40, db_column=u'County2Name')
    main_association_id = models.IntegerField(null=True, db_column=u'District1')
    local_association_id = models.IntegerField(null=True, db_column=u'District2')
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
