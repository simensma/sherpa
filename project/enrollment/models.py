from django.db import models

from page.models import Variant

# Has always only *one* row
class State(models.Model):
    active = models.BooleanField()
    card = models.BooleanField() # Accept card-payment
