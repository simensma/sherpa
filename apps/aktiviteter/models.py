# encoding: utf-8
from datetime import date, datetime
import json

from django.contrib.gis.db import models
from django.conf import settings
from django.core.urlresolvers import reverse

from djorm_pgarray.fields import TextArrayField

from core.util import s3_bucket
from sherpa2.models import Turforslag, ActivityDate
from turbasen.models import Omrade

class Aktivitet(models.Model):
    # Note that *either* forening or forening_cabin should be defined at any time
    forening = models.ForeignKey('foreninger.Forening', null=True, related_name='+')
    forening_cabin = models.ForeignKey('aktiviteter.Cabin', null=True, related_name='+')
    co_foreninger = models.ManyToManyField('foreninger.Forening', null=True, related_name='aktiviteter')
    co_foreninger_cabin = models.ManyToManyField('aktiviteter.Cabin', null=True, related_name='+')

    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_point = models.PointField(null=True)
    counties = models.ManyToManyField('core.County', related_name='aktiviteter')
    municipalities = models.ManyToManyField('core.Municipality', related_name='aktiviteter')
    # Array field of object ids related to the 'områder' datatype in Nasjonal Turbase
    omrader = TextArrayField(default=[])
    getting_there = models.TextField()
    turforslag = models.IntegerField(null=True) # Cross-DB relationship to sherpa2.models.Turforslag
    DIFFICULTY_CHOICES = (
        ('easy', 'Enkel'),
        ('medium', 'Middels'),
        ('hard', 'Krevende'),
        ('expert', 'Ekspert'),)
    difficulty = models.CharField(max_length=255, choices=DIFFICULTY_CHOICES)
    audiences = models.ManyToManyField('aktiviteter.AktivitetAudience', related_name='aktiviteter')
    CATEGORY_CHOICES = (
        ('organizedhike', 'Fellestur'),
        ('course', 'Kurs'),
        ('event', 'Arrangement'),
        ('volunteerwork', 'Dugnad'),)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    # Note that while a value for category_type is required in the admin UI, there could still exists objects
    # without a value if:
    # - This is a new object created when opening the edit-form, but hasn't been saved
    # - It's an imported aktivitet from sherpa 2 - not all of these have a category_type and we've chosen to ignore
    #   them
    category_type = models.CharField(max_length=255, default='')
    category_tags = models.ManyToManyField('core.Tag', related_name='aktiviteter')
    pub_date = models.DateField()
    published = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    # Applicable for aktiviteter imported from sherpa2
    sherpa2_id = models.IntegerField(null=True)

    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.title)

    def get_co_foreninger_mixed(self):
        """Returns a list of foreninger and/or cabins related to this aktivitet"""
        return list(self.co_foreninger.all()) + list(self.co_foreninger_cabin.all())

    def get_dates_ordered(self):
        return enumerate(self.dates.all().order_by('start_date'))

    def get_difficulty(self):
        return [c[1] for c in self.DIFFICULTY_CHOICES if c[0] == self.difficulty][0]

    def get_start_point_latlng(self):
        return ','.join(str(i) for i in self.start_point.get_coords()) if self.start_point else ''

    def get_start_point_lat_json(self):
        return json.dumps(self.start_point.get_coords()[0])

    def get_start_point_lng_json(self):
        return json.dumps(self.start_point.get_coords()[1])

    def get_omrader(self):
        return [Omrade.get(object_id=object_id) for object_id in self.omrader]

    def get_audiences(self):
        return [a.name for a in self.audiences.all()]

    def get_category(self):
        return [c for c in self.CATEGORY_CHOICES if c[0] == self.category][0][1]

    def get_main_category_types(self):
        return [{
            'name': sub,
            'category': self.category,
            'active': sub in self.get_active_category_types()
        } for sub in Aktivitet.CATEGORY_TYPES[self.category]]

    def get_other_category_types(self):
        other_category_types = []
        for category, category_types in Aktivitet.CATEGORY_TYPES.items():
            if category == self.category:
                continue

            for category_type in category_types:
                other_category_types.append({
                    'name': category_type,
                    'category': category,
                    'active': category_type in self.get_active_category_types()
                })

        all_category_types = []
        for types in Aktivitet.CATEGORY_TYPES.values():
            for type in types:
                all_category_types.append(type)

        for category_type in self.get_active_category_types():
            if category_type not in all_category_types:
                other_category_types.append({
                    'name': category_type,
                    'category': 'custom',
                    'active': True
                })

        return other_category_types

    def has_other_category_types(self):
        return any([s['active'] for s in self.get_other_category_types()])

    def get_active_category_types(self):
        return [t.name for t in self.category_tags.all()]

    def get_turforslag(self):
        if self.turforslag is None:
            return None
        else:
            return Turforslag.objects.get(id=self.turforslag)

    def get_images_ordered(self):
        return self.images.order_by('order')

    def get_images_ordered_enumerated(self):
        return enumerate(self.images.order_by('order'))

    def get_image(self):
        try:
            # Note that selecting all will help avoid extra queries if the images have been prefetched
            return self.images.all()[0]
        except IndexError:
            return None

    def get_images_json(self):
        images = []
        for image in self.images.order_by('order'):
            images.append({
                'url': image.url,
                'text': image.text,
                'photographer': image.photographer,
                'order': image.order,
            })
        return json.dumps(images)

    def is_published(self):
        today = date.today()
        return self.pub_date <= today

    def is_imported(self):
        return self.sherpa2_id is not None

    @staticmethod
    def get_published():
        today = date.today()
        return Aktivitet.objects.filter(published=True, pub_date__lte=today)

    # A predefined list of category type suggestions - they're simply implemented
    # as tags ('core.Tag'), though.
    CATEGORY_TYPES_LIST = [
        {
            'category': 'organizedhike',
            'types': [
                u'fottur',
                u'skitur',
                u'sykkeltur',
                u'padletur',
                u'klatretur',
                u'bretur'
            ],
        }, {
            'category': 'course',
            'types': [
                u'turlederkurs',
                u'instruktørkurs',
                u'brekurs',
                u'klatrekurs',
                u'skredkurs',
                u'gps-kurs',
                u'kajakkurs',
                u'førstehjelpskurs',
            ],
        }, {
            'category': 'event',
            'types': [
                u'kom-deg-ut-dagen',
                u'basecamp',
                u'opptur',
                u'oppstart',
                u'fjellsportsamling',
                u'sommeråpning',
                u'konsert',
                u'festival',
                u'medlemsmøte',
                u'foredrag',
                u'familieleir',
                u'barneleir',
            ],
        }, {
            'category': 'volunteerwork',
            'types': [
                u'merking',
                u'varding',
                u'rydding',
                u'snekring',
                u'maling',
                u'vedlikeholdsarbeid',
                u'turledelse',
                u'organisasjonsarbeid',
                u'arrangementsbistand',
            ],
        }
    ]

    # A dictionary structure of the same data
    CATEGORY_TYPES = {
        category['category']: category['types']
        for category in CATEGORY_TYPES_LIST
    }


class AktivitetDate(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='dates')
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField()
    signup_enabled = models.BooleanField(default=True)
    signup_montis = models.BooleanField(default=False)
    signup_simple_allowed = models.BooleanField(default=False)
    signup_max_allowed = models.PositiveIntegerField(default=0, null=True)

    # If signup_enabled is False, these values are not applicable and should always be null
    # If signup_enabled is True, null means that there are no deadlines, signup & cancel should always be available
    signup_start = models.DateField(null=True)
    signup_deadline = models.DateField(null=True)
    cancel_deadline = models.DateField(null=True)

    should_have_turleder = models.BooleanField(default=False)
    turledere = models.ManyToManyField('user.User', related_name='turleder_aktivitet_dates')
    participants = models.ManyToManyField('user.User', related_name='aktiviteter')
    meeting_place = models.TextField()
    meeting_time = models.DateTimeField(null=True)
    CONTACT_TYPE_CHOICES = (
        (u'arrangør', 'Arrangørforening'),
        (u'turleder', 'Turleder'),
        (u'custom', 'Skriv inn'),)
    contact_type = models.CharField(max_length=255, choices=CONTACT_TYPE_CHOICES, default=u'arrangør')
    contact_custom_name = models.CharField(max_length=255)
    contact_custom_phone = models.CharField(max_length=255)
    contact_custom_email = models.CharField(max_length=255)

    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s (%s, aktivitet: <%s>)' % (self.pk, self.start_date, self.aktivitet)

    #
    # Signup methods
    #

    def has_departed(self):
        return self.start_date < datetime.today()

    def has_returned(self):
        return self.end_date < datetime.today()

    def signup_method(self):
        if not self.signup_enabled:
            return 'none'
        else:
            if self.signup_montis:
                return 'montis'
            elif self.signup_simple_allowed:
                return 'simple'
            else:
                return 'minside'

    def signup_starts_immediately(self):
        return self.signup_enabled and self.signup_start is None

    def signup_available_to_departure(self):
        return self.signup_enabled and self.signup_deadline is None

    def cancel_deadline_always_available(self):
        return self.signup_enabled and self.cancel_deadline is None

    def accepts_signups(self):
        if not self.signup_enabled:
            return False

        today = date.today()

        if not self.signup_starts_immediately() and self.signup_start > today:
            # Signup not open yet
            return False

        if not self.signup_available_to_departure() and self.signup_deadline < today:
            # Signup deadline has passed
            return False

        if today > self.start_date.date():
            # Departure was yesterday, signup is now closed regardless of the deadlines
            # Note that we're not accounting for the start hour for now. If we want to, we'll have to handle
            # imported aktiviteter as they're all set to 00:00 and signup shouldn't close until the day has passed for
            # them.
            return False

        # All guards passed
        return True

    def will_accept_signups(self):
        """Returns True if this date does NOT currently accept signups, but will in the future"""
        if not self.signup_enabled:
            return False

        return not self.signup_starts_immediately() and self.signup_start >= date.today()

    def signup_deadline_passed(self):
        if not self.signup_enabled:
            return False

        return not self.signup_available_to_departure() and self.signup_deadline < date.today()

    def accepts_signup_cancels(self):
        if not self.signup_enabled:
            return False

        return self.cancel_deadline_always_available() or self.cancel_deadline >= date.today()

    def signup_url(self):
        if self.signup_montis:
            return 'https://booking.dntoslo.no/finn-avgang/%s/%s' % (
                self.aktivitet.code,
                self.start_date.strftime('%Y/%m/%d'),
            )

        if self.aktivitet.is_imported():
            return u'%s/booking.php?ac_id=%s&ac_date_from=%s' % (
                self.aktivitet.forening.get_main_foreninger()[0].get_old_url(),
                self.aktivitet.sherpa2_id,
                self.start_date.strftime('%Y-%m-%d'),
            )

        return reverse('aktiviteter.views.signup', args=[self.id])

    def total_signup_count(self):
        return self.participants.count() + self.simple_participants.count()

    def is_full(self):
        if self.signup_max_allowed is None:
            return False
        return self.total_signup_count() >= self.signup_max_allowed

    def is_waitinglist(self):
        if self.signup_max_allowed is None:
            return False
        return self.total_signup_count() > self.signup_max_allowed

    def total_waitinglist_count(self):
        if self.signup_max_allowed is None:
            return 0
        return self.total_signup_count() - self.signup_max_allowed


    #
    # End signup-methods
    #

    def other_dates(self):
        return self.aktivitet.dates.exclude(id=self.id)

    def get_other_dates_ordered(self):
        return self.other_dates().exclude(start_date__lt=date.today()).order_by('start_date')

    def get_future_dates_ordered(self):
        return self.aktivitet.dates.exclude(start_date__lt=date.today()).order_by('start_date')

    def get_duration_days(self):
        diff = self.end_date - self.start_date
        return diff.days

    def get_duration_hours(self):
        diff = self.end_date - self.start_date
        return diff.seconds / 3600

    def get_duration(self):
        diff = self.end_date - self.start_date
        days = diff.days

        if diff.total_seconds() == 0:
            return u'1 dag'
        elif days == 0:
            hours = diff.seconds / 3600
            return u'%s timer' % (hours)
        else:
            # Huh? What?! Did you just add an extra day? Yes, I did. We need to round up the number
            # of days to avoid confusion. A trip from a friday to a sunday is not 3 full days but,
            # but it is though of as a 3 day hike.
            return u'%s dager' % (days + 1)

    def get_turledere_ordered(self):
        return sorted(self.turledere.all(), key=lambda p: p.get_first_name())

    #
    # Temporary Sherpa2 methods
    #

    def get_sherpa2_date(self):
        """Returns the corresponding date object in sherpa2. It is not guaranteed to exist."""
        return ActivityDate.objects.get(
            activity__id=self.aktivitet.sherpa2_id,
            date_from=self.start_date.strftime('%Y-%m-%d'),
            date_to=self.end_date.strftime('%Y-%m-%d'),
        )

    def is_waitinglist_sherpa2(self):
        try:
            return self.get_sherpa2_date().is_waitinglist()
        except ActivityDate.DoesNotExist:
            # Well, if the date doesn't exist, the signup button won't work anyway, this is a problem but this method
            # isn't the right place to raise any exception about that, so ignore it
            return False

    def total_signup_count_sherpa2(self):
        try:
            return self.get_sherpa2_date().participant_count()
        except ActivityDate.DoesNotExist:
            # Well, if the date doesn't exist, the signup button won't work anyway, this is a problem but this method
            # isn't the right place to raise any exception about that, so ignore it
            return 0

    #
    # End Sherpa2 methods
    #

    @staticmethod
    def get_published():
        today = date.today()
        return AktivitetDate.objects.filter(aktivitet__published=True, aktivitet__pub_date__lte=today)

# @TODO This should have a forign key to admin.Image!
class AktivitetImage(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='images')
    url = models.CharField(max_length=2048)
    text = models.CharField(max_length=1024)
    photographer = models.CharField(max_length=255)
    order = models.IntegerField()

    # If not NULL, this is an image that has been imported from Sherpa 2. The old URL reference is saved to detect
    # duplicates during subsequent imports.
    sherpa2_url = models.CharField(max_length=1023, null=True)

    DEFAULT_IMAGE_RESOLUTION = 940

    def __unicode__(self):
        return u'%s' % self.pk

    def get_optimized_url(self, min_resolution=DEFAULT_IMAGE_RESOLUTION):
        """Returns a scaled version of this image, with a minimum of the given resolution. Only images referenced
        directly from our image archive can be optimized, other references are returned as-is."""
        # Note that we're ignoring debug context since the image references will have been saved with the prod-bucket,
        # and that's what we want to compare.
        local_image_path = '%s/%s' % (s3_bucket(ignore_debug=True), settings.AWS_IMAGEGALLERY_PREFIX)
        local_image_path_ssl = '%s/%s' % (s3_bucket(ssl=True, ignore_debug=True), settings.AWS_IMAGEGALLERY_PREFIX)

        if local_image_path not in self.url and local_image_path_ssl not in self.url:
            # Not an image from the image gallery; don't touch it
            return self.url

        for size in settings.THUMB_SIZES:
            if ('-%s') % size in self.url:
                # The image URL contains an explicit size, probably intentional - use it as-is
                return self.url

        if min_resolution > max(settings.THUMB_SIZES):
            # No thumbs are large enough, use the original
            return self.url
        else:
            thumb_size = min([t for t in settings.THUMB_SIZES if t >= min_resolution])

        name, extension = self.url.rsplit('.', 1)
        return '%s-%s.%s' % (name, thumb_size, extension)

    class Meta:
        ordering = ['order']

class AktivitetAudience(models.Model):
    AUDIENCE_CHOICES = (
        ('adults', 'Voksne'),
        ('children', 'Barn'),
        ('youth', 'Ungdom'),
        ('senior', 'Seniorer'),
        ('mountaineers', 'Fjellsportinteresserte'),
        ('disabled', 'Funksjonshemmede'),
    )
    name = models.CharField(max_length=255, choices=AUDIENCE_CHOICES)

    def __unicode__(self):
        return u'%s: %s' % (self.id, self.name)

class SimpleParticipant(models.Model):
    aktivitet_date = models.ForeignKey(AktivitetDate, related_name='simple_participants')
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

class Cabin(models.Model):
    """This temporary model is used to store cabin names with a relation to aktiviteter. When NTB-integration is
    implemented, this model should be replaced with references to cabins in NTB."""
    name = models.CharField(max_length=255)
    sherpa2_id = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%s/%s: %s' % (self.pk, self.sherpa2_id, self.name)

class ConversionFailure(models.Model):
    """A list of aktiviteter that we couldn't import from Sherpa2"""
    # Note that aktiviteter with no owners should be explicitly listed as they can't be filtered to any forening
    # Not quite sure why related_name can't be set to '+' here
    foreninger = models.ManyToManyField('foreninger.Forening', null=True, related_name='failed_imports')
    cabins = models.ManyToManyField('aktiviteter.Cabin', null=True, related_name='failed_imports')
    sherpa2_id = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    latest_date = models.DateField(null=True)

    # The list of reason choices should correspond to the exceptions in the sherpa2 app inheriting from
    # ConversionImpossible
    REASON_CHOICES = (
        ('owner_doesnotexist', 'Aktiviteten er koblet til en arrangør som ikke finnes i nye Sherpa'),
        ('no_owners', 'Aktiviteten har ingen arrangør.'),
        ('date_without_start_date', 'Aktiviteten har en avgang uten noen startdato.'),
        ('date_with_invalid_start_date', 'Aktiviteten har en avgang med ugyldig startdato.'),
        ('date_without_end_date', 'Aktiviteten har en avgang uten noen sluttdato.'),
        ('date_with_invalid_end_date', 'Aktiviteten har en avgang med ugyldig sluttdato.'),
    )
    reason = models.CharField(max_length=255, choices=REASON_CHOICES)

    REASON_HELPTEXTS = {
        'owner_doesnotexist':
            'Vi har flyttet alle foreninger og hytter over til nye Sherpa, men denne turen er koblet til en ' \
            'forening, hytte eller annen gruppe som ikke finnes i nye Sherpa.<br>For å få flyttet over turen ' \
            'må du finne ut hvilken gruppe som ikke skal være arrangør for turen.<br>Hvis du mener at alle ' \
            'arrangørene står riktig oppført, bør du høre med DNT Sentralt - bruk den røde knappen til høyre på ' \
            'skjermen.',
        'no_owners':
            'Alle turer må være koblet til minst én arrangørforening.',
        'date_without_start_date':
            'Sjekk datoene i bunnen av gamle Sherpa. En av linjene mangler startdato, og den må du legge inn.',
        'date_with_invalid_start_date':
            'Sjekk datoene i bunnen av gamle Sherpa. En av linjene har oppgitt startdato på feil format. Datoen må ' \
            'se slik ut: "2014-12-31".',
        'date_without_end_date':
            'Sjekk datoene i bunnen av gamle Sherpa. En av linjene mangler sluttdato, og den må du legge inn.',
        'date_with_invalid_end_date': 'Sjekk datoene i bunnen av gamle Sherpa. En av linjene har oppgitt sluttdato ' \
            'på feil format. Datoen må se slik ut: "2014-12-31".',
    }

    def get_reason(self):
        return [r[1] for r in self.REASON_CHOICES if r[0] == self.reason][0]

    def get_reason_helptext(self):
        return ConversionFailure.REASON_HELPTEXTS[self.reason]

class SynchronizationDate(models.Model):
    """Temporary model with exactly one row, denoting the time of the last successful synchronization"""
    date = models.DateTimeField()
