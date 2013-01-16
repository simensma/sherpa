from django.db import models
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache

from sherpa25.models import Member, Classified
from user.models import Profile
from core.models import County

cachedQueries = []

def invalidate_cache():
    for cacheKey in cachedQueries:
        cache.delete(cacheKey)

def getAndCacheAnnonserByFilter(minage, maxage, fylke, gender):
    #to protect the privacy of people with hidden age, min age and max age is rounded down and up to the closest 5
    #5this is to prevent "age probing" by editing the html to for instance 26-27 to determine the age of a person with hidden age

    minage = int(minage/5) * 5
    maxage =(int((maxage+5)/5) * 5)-1

    now = datetime.now();
    ninetydaysago = now - timedelta(days=90)
    #all annonser that are not hidden, is newer than 90 days, and matches the query, order by date

    cacheKey = 'fjelltreffenannonser.%s.%s.%s.%s' % (minage, maxage, fylke, gender)
    annonser = cache.get(cacheKey)
    if annonser == None:
        annonser = Annonse.objects.filter(hidden=False, timeadded__gte=ninetydaysago)
        if gender != None:
            annonser = annonser.filter(gender=gender)
        if fylke != '00':
            annonser = annonser.filter(fylke__code=fylke)
        annonser = annonser.order_by('-timeadded')
        # We'll need to filter on Focus-data in the code, since it's a cross-db relation
        annonser = [a for a in annonser if a.userprofile.get_actor().get_age() >= minage and a.userprofile.get_actor().get_age() <= maxage]

        cache.set(cacheKey, annonser, 60 * 60 * 10)
        cachedQueries.append(cacheKey)
    return annonser

def create_and_save_new_annonse_from_old_annonse(oldmember, oldannonse, oldannonseimageurl):
    annonse = Annonse()
    annonse.userprofile = Profile.objects.get(memberid=oldmember.memberid)
    annonse.timeadded = oldannonse.authorized
    annonse.title = oldannonse.title
    annonse.email = oldmember.email

    newcounty = oldannonse.county
    if newcounty < 10:
        newcounty = '0'+str(newcounty)
    else:
        newcounty = str(newcounty)
    try:
        annonse.fylke = County.objects.get(code=newcounty)
    except County.DoesNotExist:
        annonse.fylke = County.objects.get(code=annonse.userprofile.get_county())

    annonse.image = oldannonseimageurl
    annonse.text = oldannonse.content
    annonse.isold = True
    annonse.hidden = False
    annonse.hideage = True
    annonse.compute_gender()

    #hax to prevent autoadd now
    annonse.save()
    annonse.timeadded = oldannonse.authorized
    annonse.save()

    #invalidates cache to prevent users from going: "where is my annonse? Better call support! Better submit new ones!"
    invalidate_cache()


class Annonse(models.Model):
    userprofile = models.ForeignKey('user.Profile')
    timeadded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    fylke = models.ForeignKey('core.County')
    image = models.CharField(max_length=2048, null=True)
    text = models.TextField()
    hidden = models.BooleanField()
    hideage = models.BooleanField()
    #Male ->True, female -> False
    gender = models.BooleanField()
    isold = models.BooleanField()

    def get_image_url(self):
        if isold:
            return settings.OLD_SITE + image;
        else:
            return settings.AWS_BUCKET + '/' + settings.AWS_IMAGEGALLERY_PREFIX + image

    def get_age(self):
        age = self.userprofile.get_actor().get_age()
        if self.hideage:
            return '%s-%s' % (int(age/5) * 5, (int((age+5)/5) * 5)-1)
        else:
            return age

    def get_gender(self):
        if self.gender == True:
            return 'Mann'
        else:
            return "Kvinne"

    def compute_gender(self):
        actor = self.userprofile.get_actor()
        if actor == None:
            self.gender = False
            return

        if actor.sex == 'M':
            self.gender = True
        else:
            self.gender = False
