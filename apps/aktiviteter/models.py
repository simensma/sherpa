# encoding: utf-8
from django.contrib.gis.db import models

from datetime import date
import json

class Aktivitet(models.Model):
    association = models.ForeignKey('association.Association', related_name='+')
    co_association = models.ForeignKey('association.Association', null=True, related_name='+')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_point = models.PointField(null=True)
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

    def get_dates_ordered(self):
        return self.dates.all().order_by('-start_date')

    def get_difficulty(self):
        return [c[1] for c in self.DIFFICULTY_CHOICES if c[0] == self.difficulty][0]

    def get_start_point_lat_json(self):
        return json.dumps(self.start_point.get_coords()[0])

    def get_start_point_lng_json(self):
        return json.dumps(self.start_point.get_coords()[1])

    def get_audiences(self):
        return json.loads(self.audiences)

    def get_category(self):
        return [c[1] for c in self.CATEGORY_CHOICES if c[0] == self.category][0]

    def get_subcategories(self):
        return self.SUBCATEGORIES[self.category]

    def get_missing_subcategories(self):
        existing_subcategories = [s.name for s in self.category_tags.all()]
        return [s for s in self.get_subcategories() if s not in existing_subcategories]

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
    signup_start = models.DateField()
    signup_deadline = models.DateField()
    signup_cancel_deadline = models.DateField()
    new_leaders = models.ManyToManyField('user.User', related_name='new_leader_aktivitet_dates')
    new_participants = models.ManyToManyField('user.User', related_name='new_aktiviteter')

    def get_signup_enabled_json(self):
        return json.dumps(self.signup_enabled)

    def accepts_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start <= today and self.signup_deadline >= today

    def will_accept_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start > today

    def accepts_signup_cancels(self):
        today = date.today()
        return self.signup_enabled and self.signup_cancel_deadline >= today

    def other_dates(self):
        return self.aktivitet.dates.exclude(id=self.id)

    def get_other_dates_ordered(self):
        return self.other_dates().order_by('-start_date')

    def get_leaders_ordered(self):
        return sorted(self.leaders.all(), key=lambda p: p.get_first_name())

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
