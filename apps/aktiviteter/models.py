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
        ('trip', 'Tur'),
        ('course', 'Kurs'),)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    tags = models.ManyToManyField('core.Tag', related_name='aktiviteter')
    pub_date = models.DateField()
    hidden = models.BooleanField(default=False)

    def get_dates_ordered(self):
        return self.dates.all().order_by('-start_date')

    def get_difficulty(self):
        return [c[1] for c in self.DIFFICULTY_CHOICES if c[0] == self.difficulty][0]

    def get_category(self):
        return [c[1] for c in self.CATEGORY_CHOICES if c[0] == self.category][0]

class AktivitetDate(models.Model):
    aktivitet = models.ForeignKey(Aktivitet, related_name='dates')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    signup_enabled = models.BooleanField(default=True)
    signup_start = models.DateField()
    signup_deadline = models.DateField()
    signup_cancel_deadline = models.DateField()
    participants = models.ManyToManyField('user.Profile', related_name='aktiviteter')

    def get_signup_enabled_json(self):
        return json.dumps(self.signup_enabled)

    def accepts_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start <= today and self.signup_deadline >= today

    def will_accept_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start > today

    def other_dates(self):
        return self.aktivitet.dates.exclude(id=self.id)

    def get_other_dates_ordered(self):
        return self.other_dates().order_by('-start_date')

    @staticmethod
    def get_published():
        today = date.today()
        return AktivitetDate.objects.filter(aktivitet__pub_date__lte=today)
