# encoding: utf-8
from django.db import models

from datetime import date
import json

class Aktivitet(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    DIFFICULTY_CHOICES = (
        ('easy', 'Enkel'),
        ('medium', 'Middels'),
        ('hard', 'Krevende'),
        ('expert', 'Ekspert'),)
    difficulty = models.CharField(max_length=255, choices=DIFFICULTY_CHOICES)
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

    def get_category(self):
        return [c[1] for c in self.CATEGORY_CHOICES if c[0] == self.category][0]

    def get_subcategories(self):
        return self.SUBCATEGORIES[self.category]

    def get_missing_subcategories(self):
        existing_subcategories = [s.name for s in self.category_tags.all()]
        return [s for s in self.get_subcategories() if s not in existing_subcategories]

    # A predefined list of subcategory suggestions - they're simply implemented
    # as tags ('core.Tag'), though.
    SUBCATEGORIES = {
        'trip': [
            'fottur',
            'skitur',
            'sykkeltur',
            'klatring',
            'padling',
            'skøytetur',
            'topptur',
            'kiting',
            'surfing',
            'brevandring',
            'grottetur',
            'snøhuletur',
            'trilletur',
            'bærtur',
            'sopptur',
            'fisketur',
            'ridetur',
            'singeltur',
            'naturlos',
            'utenlandstur',
            'orientering',
        ],
        'course': [
            'turlederkurs',
            'instruktørkurs',
            'brekurs',
            'klatrekurs',
            'skredkurs',
            'gps-kurs',
            'kajakkurs',
            'førstehjelpskurs',
        ],
        'event': [
            'kom-deg-ut-dagen',
            'basecamp',
            'opptur',
            'oppstart',
            'fjellsportsamling',
            'sommeråpning',
            'konsert',
            'festival',
            'medlemsmøte',
            'foredrag',
            'familieleir',
            'barneleir',
        ],
        'volunteerwork': [
            'merking',
            'varding',
            'rydding',
            'snekring',
            'maling',
            'vedlikeholdsarbeid',
            'turledelse',
            'organisasjonsarbeid',
            'arrangementsbistand',
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
    leaders = models.ManyToManyField('user.Profile', related_name='+')
    participants = models.ManyToManyField('user.Profile', related_name='aktiviteter')

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
