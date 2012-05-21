from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)
    text = models.CharField(max_length=200)
    # Much more person data

class Zipcode(models.Model):
    zip_code = models.CharField(max_length=4)
    location = models.CharField(max_length=100)
    city_code = models.CharField(max_length=4)
    city = models.CharField(max_length=100)

class County(models.Model):
    code = models.CharField(max_length=2)
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
