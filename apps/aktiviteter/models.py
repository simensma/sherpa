from django.db import models

from datetime import date
import json

class Aktivitet(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tags = models.ManyToManyField('core.Tag', related_name='aktiviteter')
    signup_enabled = models.BooleanField(default=True)
    signup_start = models.DateField()
    signup_deadline = models.DateField()
    signup_cancel_deadline = models.DateField()
    participants = models.ManyToManyField('user.Profile', related_name='aktiviteter')
    hidden = models.BooleanField(default=False)

    def get_signup_enabled_json(self):
        return json.dumps(self.signup_enabled)

    def accepts_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start <= today and self.signup_deadline >= today

    def will_accept_signups(self):
        today = date.today()
        return self.signup_enabled and self.signup_start > today
