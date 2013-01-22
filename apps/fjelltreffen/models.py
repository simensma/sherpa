from django.db import models
from django.conf import settings
from django.core.cache import cache

from datetime import datetime, timedelta

class Annonse(models.Model):
    profile = models.ForeignKey('user.Profile')
    timeadded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    fylke = models.ForeignKey('core.County')
    image = models.CharField(max_length=2048)
    text = models.TextField()
    hidden = models.BooleanField()
    hideage = models.BooleanField()
    isold = models.BooleanField()

    def get_image_url(self):
        if self.isold:
            return "http://%s/%s" % (settings.OLD_SITE, self.image);
        else:
            return "http://%s/%s/%s" % (settings.AWS_BUCKET, settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, self.image)

    def get_age(self):
        age = self.profile.get_actor().get_age()
        if self.hideage:
            return '%s-%s' % (int(age/5) * 5, (int((age+5)/5) * 5)-1)
        else:
            return age

    def is_expired(self):
        return self.timeadded < (datetime.now() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS))

#
# Utility methods
#

def get_annonser_by_filter(minage, maxage, fylke, gender):
    #to protect the privacy of people with hidden age, min age and max age is rounded down and up to the closest 5
    #5this is to prevent "age probing" by editing the html to for instance 26-27 to determine the age of a person with hidden age

    minage = int(minage/5) * 5
    maxage =(int((maxage+5)/5) * 5)-1

    now = datetime.now();
    active_period = now - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)
    #all annonser that are not hidden, is newer than X days, and matches the query, order by date

    annonser = Annonse.objects.filter(hidden=False, timeadded__gte=active_period)
    if fylke != '00':
        annonser = annonser.filter(fylke__code=fylke)
    annonser = annonser.order_by('-timeadded')
    # We'll need to filter on Focus-data in the code, since it's a cross-db relation
    annonser = [a for a in annonser if a.profile.get_actor().get_age() >= minage and a.profile.get_actor().get_age() <= maxage]
    if gender != '':
        annonser = [a for a in annonser if a.profile.get_actor().get_gender() == gender]

    return annonser
