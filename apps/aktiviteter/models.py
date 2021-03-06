# encoding: utf-8
from datetime import date, datetime
import json

from django.contrib.gis.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache

from djorm_pgarray.fields import TextArrayField

from core.util import s3_bucket
from sherpa2.models import Turforslag, ActivityDate
from turbasen.models import Omrade
from montis.models import Aktivitet as MontisAktivitet

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

    # All imported aktiviteter will have their signup system and participants in Sherpa 2 by default. When ready to
    # deploy the new admin and signup system, this field will be set to False, the import will stop syncing this
    # aktivitet, and all administration is from now done through Sherpa 3. Although this isn't applicable for
    # aktiviteter created in Sherpa 3, it's still set to False for them (instead of null which could be considered
    # more semantically correct).
    # TODO: Above comment is the general idea, but not implemented (the field is currently false for all objects and
    # not in use)
    sherpa2_signup = models.BooleanField(default=False)

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

    # If there are this many or fewer spots available, it signifies that the date is almost fully booked
    HIGHEST_ALMOST_FULL_COUNT = 3

    aktivitet = models.ForeignKey(Aktivitet, related_name='dates')

    # Start/end dates for this object
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField()

    # Where and when to meet
    meeting_place = models.TextField()
    meeting_time = models.DateTimeField(null=True)

    #
    # Contact details
    #

    CONTACT_TYPE_CHOICES = (
        (u'arrangør', 'Arrangørforening'),
        (u'turleder', 'Turleder'),
        (u'custom', 'Skriv inn'),
    )
    contact_type = models.CharField(max_length=255, choices=CONTACT_TYPE_CHOICES, default=u'arrangør')
    contact_custom_name = models.CharField(max_length=255)
    contact_custom_phone = models.CharField(max_length=255)
    contact_custom_email = models.CharField(max_length=255)

    #
    # Signup options
    #

    # Signup may be completely disabled by setting this to False
    signup_enabled = models.BooleanField(default=True)

    # signup_montis should be True only for DNT Oslo og Omegns aktiviteter, for whom signups are handled by an external
    # system. Setting this to True renders other signup options moot.
    signup_montis = models.BooleanField(default=False)

    # Simple signup was the first attempt of an option requiring less details from participants - due to change.
    signup_simple_allowed = models.BooleanField(default=False)

    # How many participants are allowed to sign up for this trip? NULL means unlimited.
    max_participants = models.PositiveIntegerField(default=0, null=True)

    # If signup_enabled is False, these values are not applicable and should always be null
    # If signup_enabled is True, null means that there are no deadlines, signup & cancel should always be available
    signup_start = models.DateField(null=True)
    signup_deadline = models.DateField(null=True)
    cancel_deadline = models.DateField(null=True)

    # Turledere
    should_have_turleder = models.BooleanField(default=False)
    turledere = models.ManyToManyField('user.User', related_name='turleder_aktivitet_dates')

    # Participants
    participants = models.ManyToManyField('user.User', related_name='aktiviteter')

    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s (%s, aktivitet: <%s>)' % (self.pk, self.start_date, self.aktivitet)

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
    # Signup methods (common)
    #

    def has_departed(self):
        if self.aktivitet.is_imported():
            # Dates imported from sherpa2 don't have the time of day for departure recorded, so don't assume it's
            # departed until midnight after the set departure date
            return self.start_date.date() < date.today()
        else:
            return self.start_date < datetime.now()

    def has_returned(self):
        if self.aktivitet.is_imported():
            # Dates imported from sherpa2 don't have the time of day for departure recorded, so don't assume it's
            # returned until midnight after the set return date
            return self.end_date.date() < date.today()
        else:
            return self.end_date < datetime.now()

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

    #
    # Signup methods that vary with what kind of signup this is (normal, sherpa2, montis)
    #

    def signup_method(self):
        if not self.signup_enabled:
            return 'none'
        else:
            if self.signup_montis:
                return 'montis'
            elif self.signup_simple_allowed:
                # TODO: The simple signup method is due to be removed. Instead, an option for requiring contact
                # information (or not) will be added, and that will only be applicable for normal signups.
                return 'simple'
            else:
                return 'normal'

    def _call_signup_dynamically(self, method, *args, **kwargs):
        try:
            signup_method = self.signup_method()

            # Temporary override - normal signup and imported always means sherpa2 for now
            if signup_method == 'normal' and self.aktivitet.is_imported():
                signup_method = 'sherpa2'

            return getattr(self, '_%s_%s' % (method, signup_method))(*args, **kwargs)
        except AttributeError:
            raise NotImplementedError("Haven't yet implemented method '%s' for signup method '%s'" % (
                method,
                signup_method,
            ))

    # The following methods define the publicly available methods that change behavior based on the signup method.
    # E.g. the signup_url method will call _signup_url_normal for normal signups. See the signup_method method for
    # which signup methods are available.

    def signup_url(self, *args, **kwargs):
        return self._call_signup_dynamically('signup_url', *args, **kwargs)

    def participant_count(self, *args, **kwargs):
        return self._call_signup_dynamically('participant_count', *args, **kwargs)

    def is_fully_booked(self, *args, **kwargs):
        return self._call_signup_dynamically('is_fully_booked', *args, **kwargs)

    def waitinglist_count(self, *args, **kwargs):
        return self._call_signup_dynamically('waitinglist_count', *args, **kwargs)

    def max_participant_count(self, *args, **kwargs):
        return self._call_signup_dynamically('max_participant_count', *args, **kwargs)

    def spots_available(self, *args, **kwargs):
        return self._call_signup_dynamically('spots_available', *args, **kwargs)

    #
    # Implementations for normal signups handled in Sherpa 3
    #

    def _signup_url_normal(self):
        return reverse('aktiviteter.views.signup', args=[self.id])

    def _participant_count_normal(self):
        return self.participants.count() + self.simple_participants.count()

    def _is_fully_booked_normal(self):
        if self.max_participants is None:
            return False
        return self.participant_count() >= self.max_participants

    def _waitinglist_count_normal(self):
        if self.max_participants is None:
            return 0
        return self.participant_count() - self.max_participants

    def _max_participant_count_normal(self):
        return self.max_participants

    def _spots_available_normal(self):
        return self.max_participant_count() - self.participant_count()

    def is_almost_full(self):
        if self.max_participant_count() is None:
            return False
        return self.spots_available() <= AktivitetDate.HIGHEST_ALMOST_FULL_COUNT

    #
    # End signup-methods
    #

    #
    # Montis date and signup implementations
    #

    def get_montis_date(self):
        """Returns the corresponding date object in Montis. It is not guaranteed to exist."""
        aktivitet_date = cache.get('aktiviteter.dato.%s.montis' % self.id)
        if aktivitet_date is None:
            aktivitet_date = MontisAktivitet.get(self.aktivitet.code).get_date(self.start_date)
            cache.set('aktiviteter.dato.%s.montis' % self.id, aktivitet_date, 60 * 60)
        return aktivitet_date

    def _signup_url_montis(self):
        return 'https://booking.dntoslo.no/finn-avgang/%s/%s' % (
            self.aktivitet.code,
            self.start_date.strftime('%Y/%m/%d'),
        )

    def _participant_count_montis(self):
        return self.get_montis_date().participant_count()

    def _is_fully_booked_montis(self):
        return self.get_montis_date().is_fully_booked()

    def _waitinglist_count_montis(self):
        return self.get_montis_date().waitinglist_count

    def _max_participant_count_montis(self):
        return self.get_montis_date().spots_total

    def _spots_available_montis(self):
        return self.get_montis_date().spots_available

    #
    # Temporary Sherpa2 signup implementations
    #

    def get_sherpa2_date(self):
        """Returns the corresponding date object in sherpa2. It is not guaranteed to exist."""
        activity_date = cache.get('aktiviteter.dato.%s.sherpa2' % self.id)
        if activity_date is None:
            activity_date = ActivityDate.objects.get(
                activity__id=self.aktivitet.sherpa2_id,
                date_from=self.start_date.strftime('%Y-%m-%d'),
                date_to=self.end_date.strftime('%Y-%m-%d'),
            )
            cache.set('aktiviteter.dato.%s.sherpa2' % self.id, activity_date, 60 * 60)
        return activity_date

    def _signup_url_sherpa2(self):
        return u'%s/booking.php?ac_id=%s&ac_date_from=%s' % (
            self.aktivitet.forening.get_main_foreninger()[0].get_old_url(),
            self.aktivitet.sherpa2_id,
            self.start_date.strftime('%Y-%m-%d'),
        )

    # The below methods will have to handle ActivityDate.DoesNotExist. If the date doesn't exist, the signup button
    # won't work anyway, which is a problem, but these methods aren't the right place to raise any exception about
    # that, so ignore it

    def _is_fully_booked_sherpa2(self):
        try:
            return self.get_sherpa2_date().is_fully_booked()
        except ActivityDate.DoesNotExist:
            return False

    def _participant_count_sherpa2(self):
        try:
            return self.get_sherpa2_date().participant_count()
        except ActivityDate.DoesNotExist:
            return 0

    def _waitinglist_count_sherpa2(self):
        # TODO: Implement if needed
        return 0

    def _max_participant_count_sherpa2(self):
        try:
            return self.get_sherpa2_date().booking
        except ActivityDate.DoesNotExist:
            return 0

    def _spots_available_sherpa2(self):
        return self.max_participant_count() - self.participant_count()

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
