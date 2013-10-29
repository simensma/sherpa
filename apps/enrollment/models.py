# encoding: utf-8
from django.db import models

# Has always only *one* row
class State(models.Model):
    active = models.BooleanField()
    card = models.BooleanField() # Accept card-payment
