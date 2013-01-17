from django.db import models
from django.conf import settings

from user.models import Profile
from core.models import County
from fjelltreffen.models import Annonse

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
    class Meta:
        db_table = u'Member'

def import_fjelltreffen_annonser(profile):
    old_member = Member.objects.get(memberid=profile.memberid)

    for link in Link.objects.filter(fromobject='Member', fromid=old_member.id, toobject='Classified'):
        try:
            # Check for any saved images, and see if we can determine a usable path
            imageid = Link.objects.get(fromobject='Classified', fromid=link.toid, toobject='ClassifiedImage').toid
            path = Classifiedimage.objects.get(id=imageid).path
            if path.startswith('/var/www/hosts/turistforeningen.no/web/img/fjelltreff/'):
                # This one is served on the old site and still usable
                old_annonse_imageurl = path.split('/var/www/hosts/turistforeningen.no/web/')[1]
            elif path.startswith('/www/sherpa2/www/dnt/img/fjelltreff/'):
                # This one is served on the old site and still usable
                old_annonse_imageurl = path.split('/www/sherpa2/www/dnt/')[1]
            else:
                # Unknown path, or known unusable path - ignore this image.
                old_annonse_imageurl = ''
        except (Link.DoesNotExist, Classifiedimage.DoesNotExist) as e:
            old_annonse_imageurl = ''
        try:
            old_annonse = Classified.objects.get(id=link.toid)
        except Classified.DoesNotExist as e:
            continue

        annonse = Annonse()
        annonse.profile = profile
        annonse.timeadded = old_annonse.authorized
        annonse.title = old_annonse.title

        # Email is required, so make sure we find one for the old user
        if old_member.email is None or old_member.email == '':
            # Nope, it's not here. Try to get it from Focus
            focus_email = profile.get_actor().email
            if focus_email is None or focus_email == '':
                # Not in Focus either! We'll have to ignore this annonse.
                continue
            else:
                # Ok, use the focus email
                annonse.email = focus_email
        else:
            annonse.email = old_member.email

        newcounty = old_annonse.county
        if newcounty < 10:
            newcounty = '0'+str(newcounty)
        else:
            newcounty = str(newcounty)
        try:
            annonse.fylke = County.objects.get(code=newcounty)
        except County.DoesNotExist:
            annonse.fylke = County.objects.get(code=annonse.profile.get_county())

        annonse.image = old_annonse_imageurl
        annonse.text = old_annonse.content
        annonse.isold = True
        annonse.hidden = False
        annonse.hideage = True

        #hax to prevent autoadd now
        annonse.save()
        annonse.timeadded = old_annonse.authorized
        annonse.save()
