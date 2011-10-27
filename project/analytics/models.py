from django.db import models

class Visitor(models.Model):
    person = models.ForeignKey('home.Person')
    pageviews = models.ForeignKey('analytics.Pageview')

class Pageview(models.Model):
    url = models.CharField(max_length=2048)
    referrer = models.CharField(max_length=2048)
    events = models.ForeignKey('analytics.Event')
    enter = models.DateField()
    exit = models.DateField(null=True)

class Event(models.Model):
    action = models.CharField(max_length=4096) # ?
    params = models.CharField(max_length=4096) # ?
    time = models.DateField()

class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
