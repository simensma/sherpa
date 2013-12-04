# encoding: utf-8
from django.contrib.gis.db import models

from datetime import date
import json

from sherpa2.models import Location

class Aktivitet(models.Model):
    association = models.ForeignKey('association.Association', related_name='+')
    co_association = models.ForeignKey('association.Association', null=True, related_name='+')
    code = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_point = models.PointField(null=True)
    counties = models.ManyToManyField('core.County', related_name='aktiviteter')
    municipalities = models.ManyToManyField('core.Municipality', related_name='aktiviteter')
    # 'locations' is a cross-db relationship, so store a JSON list of related IDs without DB-level constraints
    locations = models.CharField(max_length=4091)
    getting_there = models.TextField()
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
        ('trip', 'Tur/Aktivitet'),
        ('course', 'Kurs'),
        ('event', 'Arrangement'),
        ('volunteerwork', 'Dugnad'),)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    category_tags = models.ManyToManyField('core.Tag', related_name='aktiviteter')
    pub_date = models.DateField()
    hidden = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.title)

    def get_dates_ordered(self):
        return self.dates.all().order_by('-start_date')

    def get_difficulty(self):
        return [c[1] for c in self.DIFFICULTY_CHOICES if c[0] == self.difficulty][0]

    def get_start_point_lat_json(self):
        return json.dumps(self.start_point.get_coords()[0])

    def get_start_point_lng_json(self):
        return json.dumps(self.start_point.get_coords()[1])

    def get_locations(self):
        return Location.objects.filter(id__in=json.loads(self.locations))

    def get_audiences(self):
        return json.loads(self.audiences)

    def get_category(self):
        return [c for c in self.CATEGORY_CHOICES if c[0] == self.category][0]

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

    def get_images_ordered(self):
        return self.images.order_by('order')

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

    @staticmethod
    def get_published():
        today = date.today()
        return Aktivitet.objects.filter(pub_date__lte=today)

    # A predefined list of subcategory suggestions - they're simply implemented
    # as tags ('core.Tag'), though.
    SUBCATEGORIES = {
        'trip': [
            u'fottur',
            u'skitur',
            u'sykkeltur',
            u'klatring',
            u'padling',
            u'skøytetur',
            u'topptur',
            u'kiting',
            u'surfing',
            u'brevandring',
            u'grottetur',
            u'snøhuletur',
            u'trilletur',
            u'bærtur',
            u'sopptur',
            u'fisketur',
            u'ridetur',
            u'singeltur',
            u'naturlos',
            u'utenlandstur',
            u'orientering',
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

    # Signup start/deadline/cancel should only be null when signup_enabled is False
    signup_start = models.DateField(null=True)
    signup_deadline = models.DateField(null=True)
    signup_cancel_deadline = models.DateField(null=True)

    turledere = models.ManyToManyField('user.User', related_name='turleder_aktivitet_dates')
    participants = models.ManyToManyField('user.User', related_name='aktiviteter')
    meeting_place = models.TextField()
    CONTACT_TYPE_CHOICES = (
        (u'arrangør', 'Arrangørforening'),
        (u'turleder', 'Turleder'),
        (u'custom', 'Skriv inn'),)
    contact_type = models.CharField(max_length=255, choices=CONTACT_TYPE_CHOICES, default=u'arrangør')
    contact_custom_name = models.CharField(max_length=255)
    contact_custom_phone = models.CharField(max_length=255)
    contact_custom_email = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s (%s, aktivitet: <%s>)' % (self.pk, self.start_date, self.aktivitet)

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

    def other_dates(self):
        return self.aktivitet.dates.exclude(id=self.id)

    def get_other_dates_ordered(self):
        return self.other_dates().order_by('-start_date')

    def get_turledere_ordered(self):
        return sorted(self.turledere.all(), key=lambda p: p.get_first_name())

    def total_signup_count(self):
        return self.participants.count() + self.simple_participants.count()

    @staticmethod
    def get_published():
        today = date.today()
        return AktivitetDate.objects.filter(aktivitet__pub_date__lte=today)

class AktivitetImage(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='images')
    url = models.CharField(max_length=2048)
    text = models.CharField(max_length=1024)
    photographer = models.CharField(max_length=255)
    order = models.IntegerField()

    def __unicode__(self):
        return u'%s' % self.pk

class SimpleParticipant(models.Model):
    aktivitet_date = models.ForeignKey(AktivitetDate, related_name='simple_participants')
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)
