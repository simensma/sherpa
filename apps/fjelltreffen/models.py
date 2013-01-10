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
    now = datetime.now();
    ninetydaysago = now - timedelta(days=90)
    #all annonser that are not hidden, is newer than 90 days, and matches the query, order by date

    cacheKey = 'fjelltreffenannonser' + str(minage) + str(maxage) + str(fylke) + str(gender)
    annonser = cache.get(cacheKey)
    if annonser == None:
        annonser = Annonse.objects.filter(hidden=False, age__gte=minage, age__lte=maxage, timeadded__gte=ninetydaysago)
        if gender != None:
            annonser = annonser.filter(gender=gender)
        if fylke != '00':
            annonser = annonser.filter(fylke__code=fylke)
        annonser = annonser.order_by('-timeadded')

        cache.set(cacheKey, annonser, 60 * 60)
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
    print newcounty
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
    annonse.compute_age()

    #hax to prevent autoadd
    annonse.save()
    annonse.timeadded = oldannonse.authorized
    annonse.save()
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
    age = models.IntegerField()
    #Male ->True, female -> False
    gender = models.BooleanField()
    isold = models.BooleanField()

    def get_image_url(self):
        if isold:
            return settings.OLD_SITE + image;
        else:
            return settings.AWS_BUCKET + '/' + settings.AWS_IMAGEGALLERY_PREFIX + image

    def get_age(self):
        if self.hideage:
            return '' + str(int(self.age/5) * 5) + '-' + str((int((self.age+5)/5) * 5)-1)
        else:
            return self.age

    def get_date(self):
        return timeadded.day + '.' + timeadded.month + '.' + timeadded.year

    def get_gender(self):
        if self.gender == True:
            return 'Mann'
        else:
            return "Kvinne"

    def compute_gender(self):
        actor = self.userprofile.actor()
        if actor == None:
            print 'no actor'
            self.gender = False
            return

        if actor.sex == 'M':
            self.gender = True
        else:
            self.gender = False

    def compute_age(self):
        actor = self.userprofile.actor()
        if actor == None:
            self.age = 18
            self.save()
            return
        born = self.userprofile.actor().birth_date
        now = datetime.now()
        try: # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=now.year)
        except ValueError:
            birthday = born.replace(year=now.year, day=born.day-1)
        if birthday > now:
            self.age = now.year - born.year - 1
        else:
            self.age = now.year - born.year