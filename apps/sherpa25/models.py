from django.db import models

#this table links other tabels
class Link(models.Model):
    id = models.IntegerField(primary_key=True)
    fromobject = models.TextField(db_column='fromObject')
    fromid = models.IntegerField(db_column='fromId')
    toobject = models.TextField(db_column='toObject')
    toid = models.IntegerField(db_column='toId')
    role = models.IntegerField()
    priority = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'Link'

class Classified(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField(blank=True)
    content = models.TextField(blank=True)
    county = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    authorized = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    online = models.NullBooleanField(blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'Classified'

class ClassifiedImage(models.Model):
    id = models.IntegerField(primary_key=True)
    path = models.TextField(blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    online = models.NullBooleanField(blank=True)

    def __unicode__(self):
        return u'%s' % self.pk

    class Meta:
        db_table = u'ClassifiedImage'

class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.TextField(db_column='firstName')
    last_name = models.TextField(db_column='lastName')
    address1 = models.TextField()
    address2 = models.TextField()
    address3 = models.TextField()
    zipcode = models.TextField(db_column='zipCode')
    ziparea = models.TextField(db_column='zipArea')
    homephone = models.TextField(db_column='homePhone')
    workphone = models.TextField(db_column='workPhone')
    cellphone = models.TextField(db_column='cellPhone')
    email = models.TextField()
    receiveemail = models.BooleanField(db_column='receiveEmail')
    password = models.TextField()
    gender = models.CharField(max_length=1, db_column='sex')
    birthdate = models.DateField(null=True, db_column='birthDate')
    countryname = models.TextField(db_column='countryName')
    countrycode = models.TextField(db_column='countryCode')
    receivesms = models.BooleanField(db_column='receiveSms')
    memberid = models.IntegerField(unique=True, null=True, db_column='memberId')
    memberparent = models.IntegerField(null=True, db_column='memberParent')
    memberrecruiter = models.IntegerField(null=True, db_column='memberRecruiter')
    membercurrentbalance = models.IntegerField(null=True, db_column='memberCurrentBalance')
    memberpreviousbalance = models.IntegerField(null=True, db_column='memberPreviousBalance')
    memberstartdate = models.DateField(null=True, db_column='memberStartDate')
    memberservices = models.TextField(db_column='memberServices')
    memberinvoicetype = models.IntegerField(null=True, db_column='memberInvoiceType')
    membergroupid = models.IntegerField(null=True, db_column='memberGroupId')
    membergroupname = models.TextField(db_column='memberGroupName')
    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    status = models.IntegerField(null=True)
    online = models.BooleanField()

    def __unicode__(self):
        return u'%s' % self.pk

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        db_table = u'Member'
