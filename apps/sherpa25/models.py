from django.db import models
from django.conf import settings

#this table links other tabels
class Link(models.Model):
    id = models.IntegerField(primary_key=True)
    fromobject = models.TextField(db_column='fromObject')
    fromid = models.IntegerField(db_column='fromId')
    toobject = models.TextField(db_column='toObject')
    toid = models.IntegerField(db_column='toId')
    role = models.IntegerField()
    priority = models.IntegerField(null=True, blank=True)
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
    class Meta:
        db_table = u'Classified'

class Classifiedimage(models.Model):
    id = models.IntegerField(primary_key=True)
    path = models.TextField(blank=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    online = models.NullBooleanField(blank=True)
    class Meta:
        db_table = u'ClassifiedImage'

def get_old_fjelltreffen_annonser(profile):
    try:
        memberid = Member.objects.get(memberid=profile.memberid).id
    except Member.DoesNotExist:
        return []
    annonseids = []
    for link in Link.objects.filter(fromobject='Member', fromid=memberid, toobject='Classified'):
        annonseids.append(link.toid)

    annonser = []
    for annonseid in annonseids:
        try:
            imageid = Link.objects.get(fromobject='Classified', fromid=annonseid, toobject='ClassifiedImage').toid
            #this assumes url on the form dnt/img/hash.jpg, which is the old sites imageurl-format
            imageurl = Classifiedimage.objects.get(id=imageid).path.split('dnt')[1]
        except (Link.DoesNotExist, Classifiedimage.DoesNotExist) as e:
            imageurl = None
        try:
            member = Member.objects.get(memberid=profile.memberid)
            annonse = Classified.objects.get(id=annonseid)
        except (Member.DoesNotExist, Classified.DoesNotExist) as e:
            return []

        annonser.append((member, annonse, imageurl))
    return annonser

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
    sex = models.CharField(max_length=1)
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
    class Meta:
        db_table = u'Member'
