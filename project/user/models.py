from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20)
    # The length h
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True, unique=True)
    password_restore_date = models.DateTimeField(null=True)
    # At some point, this model will be extended to contain member data, syncing with Focus.
    # It will also be connected with:
    # - Djangos Group model
    # - Djangos permission system.
    # - "group.Group", might need to be renamed. (Associations?)

class Zipcode(models.Model):
    zip_code = models.CharField(max_length=4)
    location = models.CharField(max_length=100)
    city_code = models.CharField(max_length=4)
    city = models.CharField(max_length=100)

class County(models.Model):
    code = models.CharField(max_length=2)
    sherpa_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)


### Focus ###

# The FocusCountry class is not actually in Focus, but its values
# (country codes) were extracted from Focus and are stored here.
class FocusCountry(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    scandinavian = models.BooleanField()

class FocusUser(models.Model):
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

class FocusActType(models.Model):
    type = models.CharField(max_length=1, primary_key=True, db_column=u'ActType')
    name = models.CharField(max_length=50, db_column=u'ActNm')
    next = models.IntegerField(db_column=u'NextNo')
    last = models.IntegerField(db_column=u'LastNo')
    class Meta:
        db_table = u'ActType'

class Actor(models.Model):
    seqno = models.AutoField(primary_key=True, db_column=u'SeqNo')
    type = models.CharField(max_length=50, db_column=u'Type')
    actno = models.IntegerField(db_column=u'ActNo')
    last_name = models.CharField(max_length=50, db_column=u'Nm', blank=True)
    first_name = models.CharField(max_length=50, db_column=u'FiNm', blank=True)
    birth_date = models.DateTimeField(null=True, db_column=u'BDt', blank=True)
    pno = models.CharField(max_length=50, db_column=u'PNo', blank=True)
    sex = models.CharField(max_length=1, db_column=u'Sex', blank=True)
    orgno = models.CharField(max_length=50, db_column=u'OrgNo', blank=True)
    ph = models.CharField(max_length=50, db_column=u'Ph', blank=True)
    fax = models.CharField(max_length=50, db_column=u'Fax', blank=True)
    mobph = models.CharField(max_length=50, db_column=u'MobPh', blank=True)
    email = models.CharField(max_length=250, db_column=u'EMail', blank=True)
    web = models.CharField(max_length=250, db_column=u'Web', blank=True)
    adtype = models.CharField(max_length=3, db_column=u'AdType', blank=True)
    note1 = models.TextField(db_column=u'Note1', blank=True)
    note2 = models.TextField(db_column=u'Note2', blank=True)
    startdt = models.DateTimeField(null=True, db_column=u'StartDt', blank=True)
    startcd = models.CharField(max_length=5, db_column=u'StartCd', blank=True)
    enddt = models.DateTimeField(null=True, db_column=u'EndDt', blank=True)
    endcd = models.CharField(max_length=5, db_column=u'EndCd', blank=True)
    payterm = models.IntegerField(db_column=u'PayTerm')
    accno = models.CharField(max_length=50, db_column=u'AccNo', blank=True)
    disc = models.SmallIntegerField(null=True, db_column=u'Disc', blank=True)
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
    optchar1 = models.CharField(max_length=10, db_column=u'OptChar1', blank=True)
    optchar2 = models.CharField(max_length=10, db_column=u'OptChar2', blank=True)
    optchar3 = models.CharField(max_length=10, db_column=u'OptChar3', blank=True)
    optchar4 = models.CharField(max_length=10, db_column=u'OptChar4', blank=True)
    optchar5 = models.CharField(max_length=10, db_column=u'OptChar5', blank=True)
    optchar6 = models.CharField(max_length=10, db_column=u'OptChar6', blank=True)
    optchar7 = models.CharField(max_length=10, db_column=u'OptChar7', blank=True)
    optchar8 = models.CharField(max_length=10, db_column=u'OptChar8', blank=True)
    optchar9 = models.CharField(max_length=10, db_column=u'OptChar9', blank=True)
    optbit1 = models.BooleanField(db_column=u'OptBit1')
    optbit2 = models.BooleanField(db_column=u'OptBit2')
    optbit3 = models.BooleanField(db_column=u'OptBit3')
    optbit4 = models.BooleanField(db_column=u'OptBit4')
    optbit5 = models.BooleanField(db_column=u'OptBit5')
    optbit6 = models.BooleanField(db_column=u'OptBit6')
    optlng1 = models.FloatField(db_column=u'OptLng1')
    optlng2 = models.FloatField(db_column=u'OptLng2')
    optlng3 = models.FloatField(db_column=u'OptLng3')
    optdate1 = models.DateTimeField(null=True, db_column=u'OptDate1', blank=True)
    optdate2 = models.DateTimeField(null=True, db_column=u'OptDate2', blank=True)
    optdate3 = models.DateTimeField(null=True, db_column=u'OptDate3', blank=True)
    optdate4 = models.DateTimeField(null=True, db_column=u'OptDate4', blank=True)
    county1 = models.CharField(max_length=50, db_column=u'County1', blank=True)
    county2 = models.CharField(max_length=50, db_column=u'County2', blank=True)
    actrel1 = models.IntegerField(db_column=u'ActRel1')
    actrel2 = models.IntegerField(db_column=u'ActRel2')
    actrel3 = models.IntegerField(db_column=u'ActRel3')
    actrel4 = models.IntegerField(db_column=u'ActRel4')
    actrel5 = models.IntegerField(db_column=u'ActRel5')
    actrel6 = models.IntegerField(null=True, db_column=u'ActRel6', blank=True)
    actrel7 = models.IntegerField(null=True, db_column=u'ActRel7', blank=True)
    actrel8 = models.IntegerField(null=True, db_column=u'ActRel8', blank=True)
    actrel9 = models.IntegerField(null=True, db_column=u'ActRel9', blank=True)
    inf1 = models.CharField(max_length=50, db_column=u'Inf1', blank=True)
    inf2 = models.CharField(max_length=50, db_column=u'Inf2', blank=True)
    inf3 = models.CharField(max_length=50, db_column=u'Inf3', blank=True)
    inf4 = models.CharField(max_length=50, db_column=u'Inf4', blank=True)
    inf5 = models.CharField(max_length=50, db_column=u'Inf5', blank=True)
    webusr = models.CharField(max_length=50, db_column=u'WebUsr', blank=True)
    webpw = models.CharField(max_length=50, db_column=u'WebPw', blank=True)
    websh = models.IntegerField(db_column=u'WebSh')
    weblang = models.CharField(max_length=5, db_column=u'WebLang', blank=True)
    webcrby = models.CharField(max_length=25, db_column=u'WebCrBy', blank=True)
    webcrdt = models.DateTimeField(null=True, db_column=u'WebCrDt', blank=True)
    crby = models.CharField(max_length=25, db_column=u'CrBy')
    crdt = models.DateTimeField(db_column=u'CrDt')
    chby = models.CharField(max_length=25, db_column=u'ChBy')
    chdt = models.DateTimeField(db_column=u'ChDt')
    class Meta:
        db_table = u'Actor'

class ActorAddress(models.Model):
    seqno = models.AutoField(primary_key=True, db_column=u'SeqNo')
    actseqno = models.ForeignKey(Actor, unique=True, db_column=u'ActSeqNo')
    actnojoin = models.IntegerField(db_column=u'ActNoJoin')
    actadtype = models.CharField(max_length=3, unique=True, db_column=u'ActAdType', blank=True)
    a1 = models.CharField(max_length=40, db_column=u'A1', blank=True)
    a2 = models.CharField(max_length=40, db_column=u'A2', blank=True)
    a3 = models.CharField(max_length=40, db_column=u'A3', blank=True)
    zipcode = models.CharField(max_length=9, db_column=u'PCode', blank=True)
    parea = models.CharField(max_length=30, db_column=u'PArea', blank=True)
    country = models.CharField(max_length=3, db_column=u'CtryCode', blank=True)
    frdt = models.DateTimeField(null=True, db_column=u'FrDt', blank=True)
    todt = models.DateTimeField(null=True, db_column=u'ToDt', blank=True)
    chby = models.CharField(max_length=50, db_column=u'ChBy', blank=True)
    chdt = models.DateTimeField(null=True, db_column=u'ChDt', blank=True)
    crby = models.CharField(max_length=50, db_column=u'CrBy', blank=True)
    crdt = models.DateTimeField(null=True, db_column=u'CrDt', blank=True)
    class Meta:
        db_table = u'ActAd'

class FocusZipcode(models.Model):
    postcode = models.CharField(max_length=9, primary_key=True, db_column=u'PostCode')
    postarea = models.CharField(max_length=40, db_column=u'PostArea')
    county1no = models.CharField(max_length=10, db_column=u'County1No', blank=True)
    county1name = models.CharField(max_length=40, db_column=u'County1Name', blank=True)
    county2no = models.CharField(max_length=10, db_column=u'County2No', blank=True)
    county2name = models.CharField(max_length=40, db_column=u'County2Name', blank=True)
    main_group_id = models.IntegerField(null=True, db_column=u'District1', blank=True)
    local_group_id = models.IntegerField(null=True, db_column=u'District2', blank=True)
    crby = models.CharField(max_length=25, db_column=u'CrBy', blank=True)
    crdt = models.DateTimeField(null=True, db_column=u'CrDt', blank=True)
    chby = models.CharField(max_length=25, db_column=u'ChBy', blank=True)
    chdt = models.DateTimeField(null=True, db_column=u'ChDt', blank=True)
    class Meta:
        db_table = u'PostalCode'

class FocusPrice(models.Model):
    group_id = models.IntegerField(primary_key=True, db_column=u'Region')
    main = models.IntegerField(null=True, db_column=u'C101', blank=True)
    student = models.IntegerField(null=True, db_column=u'C102', blank=True)
    senior = models.IntegerField(null=True, db_column=u'C103', blank=True)
    lifelong = models.IntegerField(null=True, db_column=u'C104', blank=True)
    child = models.IntegerField(null=True, db_column=u'C105', blank=True)
    school = models.IntegerField(null=True, db_column=u'C106', blank=True)
    household = models.IntegerField(null=True, db_column=u'C107', blank=True)
    unknown = models.IntegerField(null=True, db_column=u'C108', blank=True)
    class Meta:
        db_table = u'Cust_Turist_Region_PriceCode_CrossTable'
