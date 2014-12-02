# encoding: utf-8
from datetime import date
import json

from django.contrib.gis.db import models

from sherpa2.models import Location, Turforslag

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
    # 'locations' is a cross-db relationship, so store a JSON list of related IDs without DB-level constraints
    locations = models.CharField(max_length=4091)
    getting_there = models.TextField()
    turforslag = models.IntegerField(null=True) # Cross-DB relationship to sherpa2.models.Turforslag
    DIFFICULTY_CHOICES = (
        ('easy', 'Enkel'),
        ('medium', 'Middels'),
        ('hard', 'Krevende'),
        ('expert', 'Ekspert'),)
    difficulty = models.CharField(max_length=255, choices=DIFFICULTY_CHOICES)
    AUDIENCE_CHOICES = (
        ('adults', 'Voksne'),
        ('children', 'Barn'),
        ('youth', 'Ungdom'),
        ('senior', 'Seniorer'),
        ('mountaineers', 'Fjellsportinteresserte'),
        ('disabled', 'Funksjonshemmede'),)
    # audiences is multiple choice. We *could* model this with an 'audience' table
    # with one char column and a many-to-many rel, but using a json list is easier
    # and probably faster.
    audiences = models.CharField(max_length=1023)
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

    def get_locations(self):
        return Location.get_active().filter(id__in=json.loads(self.locations))

    def get_audiences(self):
        return json.loads(self.audiences)

    def get_category(self):
        return [c for c in self.CATEGORY_CHOICES if c[0] == self.category][0][1]

    def get_main_subcategories(self):
        return [{
            'name': sub,
            'category': self.category,
            'active': sub in self.get_active_subcategories()
        } for sub in Aktivitet.SUBCATEGORIES[self.category]]

    def get_other_subcategories(self):
        other_subcategories = []
        for category, subcategories in Aktivitet.SUBCATEGORIES.items():
            if category == self.category:
                continue

            for subcategory in subcategories:
                other_subcategories.append({
                    'name': subcategory,
                    'category': category,
                    'active': subcategory in self.get_active_subcategories()
                })

        all_subcategories = []
        for subs in Aktivitet.SUBCATEGORIES.values():
            for s in subs:
                all_subcategories.append(s)

        for subcategory in self.get_active_subcategories():
            if subcategory not in all_subcategories:
                other_subcategories.append({
                    'name': subcategory,
                    'category': 'custom',
                    'active': True
                })

        return other_subcategories

    def has_other_subcategories(self):
        return any([s['active'] for s in self.get_other_subcategories()])

    def get_active_subcategories(self):
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
        for image in self.images.order_by('order'):
            return image

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

    # A predefined list of subcategory suggestions - they're simply implemented
    # as tags ('core.Tag'), though.
    SUBCATEGORIES = {
        'organizedhike': [
            u'fottur',
            u'skitur',
            u'sykkeltur',
            u'padletur',
            u'klatretur',
            u'bretur'
        ],
        'course': [
            u'turlederkurs',
            u'instruktørkurs',
            u'brekurs',
            u'klatrekurs',
            u'skredkurs',
            u'gps-kurs',
            u'kajakkurs',
            u'førstehjelpskurs',
        ],
        'event': [
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
        'volunteerwork': [
            u'merking',
            u'varding',
            u'rydding',
            u'snekring',
            u'maling',
            u'vedlikeholdsarbeid',
            u'turledelse',
            u'organisasjonsarbeid',
            u'arrangementsbistand',
        ]
    }

class AktivitetDate(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='dates')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    signup_enabled = models.BooleanField(default=True)
    signup_simple_allowed = models.BooleanField()
    signup_max_allowed = models.PositiveIntegerField(default=0, null=True)

    # Signup start/deadline/cancel should only be null when signup_enabled is False
    signup_start = models.DateField(null=True)
    signup_deadline = models.DateField(null=True)
    # Rename to cancel_deadline
    signup_cancel_deadline = models.DateField(null=True)

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

    def signup_method(self):
        if not self.signup_enabled:
            return 'none'
        else:
            if self.signup_simple_allowed:
                return 'simple'
            else:
                return 'minside'

    def accepts_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start <= today and self.signup_deadline >= today

    def will_accept_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start >= today

    def signup_deadline_passed(self):
        today = date.today()
        return self.signup_enabled and self.signup_deadline < today

    def accepts_signup_cancels(self):
        today = date.today()
        return self.signup_enabled and self.signup_cancel_deadline >= today

    def external_signup_url(self):
        # @TODO check if this is a Montis signup

        if not self.aktivitet.is_imported():
            return None

        return u'%s/booking.php?ac_id=%s&ac_date_from=%s' % (
            self.aktivitet.forening.get_main_foreninger()[0].get_old_url(),
            self.aktivitet.sherpa2_id,
            self.start_date.strftime('%Y-%m-%d'),
        )

    def other_dates(self):
        return self.aktivitet.dates.exclude(id=self.id)

    def get_other_dates_ordered(self):
        return self.other_dates().order_by('-start_date')

    def get_duration_days(self):
        diff = self.end_date-self.start_date
        return diff.days

    def get_duration_hours(self):
        diff = self.end_date-self.start_date
        return diff.seconds / 3600

    def get_duration(self):
        diff = self.end_date-self.start_date
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

    @staticmethod
    def get_published():
        today = date.today()
        return AktivitetDate.objects.filter(aktivitet__published=True, aktivitet__pub_date__lte=today)

class AktivitetImage(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='images')
    url = models.CharField(max_length=2048)
    text = models.CharField(max_length=1024)
    photographer = models.CharField(max_length=255)
    order = models.IntegerField()

    # If not NULL, this is an image that has been imported from Sherpa 2. The old URL reference is saved to detect
    # duplicates during subsequent imports.
    sherpa2_url = models.CharField(max_length=1023, null=True)

    def __unicode__(self):
        return u'%s' % self.pk

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
