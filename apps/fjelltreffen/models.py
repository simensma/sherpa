from django.db import models
from django.conf import settings
from django.core.cache import cache

from datetime import datetime, timedelta

class Annonse(models.Model):
    profile = models.ForeignKey('user.Profile')
    timeadded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    county = models.ForeignKey('core.County')
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

#annonser to load when a user requests more
BULKLOADNUM = 20

def get_annonser_by_filter(minage, maxage, county, gender, start_index=0):
    #to protect the privacy of people with hidden age, min age and max age is rounded down and up to the closest 5
    #5this is to prevent "age probing" by editing the html to for instance 26-27 to determine the age of a person with hidden age

    minage = int(minage/5) * 5
    maxage =(int((maxage+5)/5) * 5)-1
    active_period = datetime.now() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)

    # Since we have to filter based on a cross-db relation, we'll have to be creative. Fetch the expected count - filter
    # over cross-db data in code - and repeat until we have the expected count or until there are none left. This is
    # absolutely not very fast, but with caching, especially of Focus Actors, it works for the amount of data/traffic we
    # have, at least for now.

    all_candidates = Annonse.objects.filter(hidden=False, timeadded__gte=active_period)
    if county != '00':
        all_candidates = all_candidates.filter(county__code=county)
    all_candidates = all_candidates.order_by('-timeadded')[start_index:]

    annonse_matches = []
    for a in all_candidates:
        start_index += 1

        if a.profile.get_actor().get_age() < minage or a.profile.get_actor().get_age() > maxage:
            continue

        if gender != '' and a.profile.get_actor().get_gender() != gender:
            continue

        annonse_matches.append(a)

        if len(annonse_matches) >= BULKLOADNUM:
            # We now have the amount of results we want
            break

    return (annonse_matches, start_index)
