from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)
    text = models.CharField(max_length=200)
    # Much more person data

class Zipcode(models.Model):
    code = models.IntegerField()
    location = models.CharField(max_length=100)
