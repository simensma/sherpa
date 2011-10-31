from django.db import models

class Visitor(models.Model):
    profile = models.ForeignKey('auth.Profile', null=True)
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

class PageVariant(models.Model):
    page = models.ForeignKey('page.Page')
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment')
    priority = models.IntegerField()
