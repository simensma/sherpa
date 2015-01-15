from datetime import date, timedelta

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings
from django.db.models import Q

import boto

from core.util import s3_bucket

# Default annonse-filters
default_min_age = '18'
default_max_age = ''    # No limit - empty string is also used in the select box
default_county = 'all'  # All counties
default_gender = ''     # All genders - empty string is also used in the select box
default_text = ''       # Text search, empty means no constraints

class Annonse(models.Model):
    user = models.ForeignKey('user.User', related_name='fjelltreffen_annonser')
    date_added = models.DateField(auto_now_add=True)
    date_renewed = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    county = models.ForeignKey('core.County', null=True) # Null means international.

    # Note that we don't enforce image uniqueness. This means that if 2 users upload the same image,
    # and one of them deletes their annonse, an invalid image reference will exist in the DB for the new one.
    image = models.CharField(max_length=2048)
    image_thumb = models.CharField(max_length=2048)

    text = models.TextField()
    hidden = models.BooleanField(default=False)
    hideage = models.BooleanField(default=False)
    is_image_old = models.BooleanField(default=False) # True for those imported from old Fjelltreffen

    def __unicode__(self):
        return u'%s' % self.pk

    def get_image_url(self):
        if self.is_image_old:
            return "http://%s/%s" % (settings.OLD_SITE, self.image)
        else:
            return "http://%s/%s/%s" % (s3_bucket(), settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, self.image)

    def get_image_thumb_url(self):
        if self.is_image_old:
            return self.get_image_url()
        else:
            return "http://%s/%s/%s" % (s3_bucket(), settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, self.image_thumb)

    def get_age(self):
        age = self.user.get_age()
        if self.hideage:
            return Annonse.obscure_age(age)
        else:
            return age

    def is_expired(self):
        return self.date_renewed < (date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS))

    def expires_in_days(self):
        return ((self.date_renewed + timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)) - date.today()).days

    def delete_image(self):
        if self.is_image_old:
            # Ignore images from old annonser, just let them rot on the old server.
            self.image = ''
            self.image_thumb = ''
            self.save()
        else:
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(s3_bucket())

            if self.image != '':
                bucket.delete_key("%s/%s" % (settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, self.image))
                self.image = ''

            if self.image_thumb != '':
                bucket.delete_key("%s/%s" % (settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, self.image_thumb))
                self.image_thumb = ''

            self.save()

    #
    # Utility methods
    #

    @staticmethod
    def obscure_age(age):
        lower = max(settings.FJELLTREFFEN_AGE_LIMITS[0], int(age / 5) * 5)
        upper = max(settings.FJELLTREFFEN_AGE_LIMITS[1], (int((age + 5) / 5) * 5) - 1)
        return '%s-%s' % (lower, upper)

    @staticmethod
    def get_active():
        active_period = date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)
        return Annonse.objects.filter(hidden=False, date_renewed__gte=active_period)

    @staticmethod
    def get_by_filter(filter, start_index=0):
        # Use provided filter, or default values if none provided
        minage = filter.get('minage', default_min_age)
        maxage = filter.get('maxage', default_max_age)
        county = filter.get('county', default_county)
        gender = filter.get('gender', default_gender)
        text = filter.get('text', default_text)

        # A strange and very rare client-side bug had the client send 'null' values for min/maxage, if it should occur
        # again just use the defaults
        if minage is None:
            minage = default_min_age
        if maxage is None:
            maxage = default_max_age

        # To protect the privacy of people with hidden age, min age and max age is rounded down and up to the closest 5
        # this is to prevent "age probing" by editing the html to for instance 26-27 to determine the age of a person with hidden age
        minage = min((abs(int(minage) - i), i) for i in settings.FJELLTREFFEN_AGE_LIMITS)[1]
        if maxage != '':
            maxage = min((abs(int(maxage) - (i - 1)), (i - 1)) for i in settings.FJELLTREFFEN_AGE_LIMITS)[1]

        # Since we have to filter based on a cross-db relation, we'll have to be creative. Fetch the expected count - filter
        # over cross-db data in code - and repeat until we have the expected count or until there are none left. This is
        # absolutely not very fast, but with caching, especially of Focus Actors, it works for the amount of data/traffic we
        # have, at least for now.

        all_candidates = Annonse.get_active()
        if county == 'all':
            # Note that this includes international annonser even though the wording says "Hele landet"
            pass
        elif county == 'international':
            all_candidates = all_candidates.filter(county__isnull=True)
        else:
            all_candidates = all_candidates.filter(county__id=county)
        if text != '':
            for word in text.split():
                all_candidates = all_candidates.filter(
                    Q(title__icontains=word) |
                    Q(text__icontains=word))
        all_candidates = all_candidates.order_by('-date_added', 'title')[start_index:]

        annonse_matches = []
        next_start_index = start_index
        for a in all_candidates:
            next_start_index += 1

            # Note - we don't account for 'hideage' when checking ages, because minage/maxage are filtered to ranges automatically.
            # If they weren't, a search where e.g. both min/max is 47, would have to match ages 45 through 49 for a user that
            # is within that range AND has hideage=True on their ad.

            if a.user.get_age() < minage:
                continue

            if maxage != '' and a.user.get_age() > maxage:
                continue

            if gender != '' and a.user.get_gender() != gender:
                continue

            annonse_matches.append(a)

            if len(annonse_matches) >= settings.FJELLTREFFEN_BULK_COUNT:
                # We now have the amount of results we want
                break

        # End is True when we've searched through all the candidates
        end = (next_start_index - start_index) == len(all_candidates)
        return (annonse_matches, next_start_index, end)

# Upon deletion, delete any stored images from S3
@receiver(pre_delete, sender=Annonse, dispatch_uid="fjelltreffen.models")
def delete_image(sender, **kwargs):
    if kwargs['instance'].image != '' or kwargs['instance'].image_thumb != '':
        kwargs['instance'].delete_image()
