from django.db import models

from page.models import Variant

# Has always only *one* row, with active True or False.
class State(models.Model):
    active = models.BooleanField()
