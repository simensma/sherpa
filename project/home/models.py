from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page')
    position = models.IntegerField()

class Person(models.Model):
    user = models.OneToOneField(User)
    # Much more person data
