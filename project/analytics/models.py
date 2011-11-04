from django.db import models

class Visitor(models.Model):
    profile = models.ForeignKey('auth.Profile', null=True)

class Pageview(models.Model):
    visitor = models.ForeignKey('analytics.Visitor')
    url = models.CharField(max_length=2048)
    referrer = models.CharField(max_length=2048)
    enter = models.DateField()
    exit = models.DateField(null=True)

class Event(models.Model):
    pageview = models.ForeignKey('analytics.PageView')
    action = models.CharField(max_length=4096) # ?
    params = models.CharField(max_length=4096) # ?
    time = models.DateField()

class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

class PageVariant(models.Model):
    version = models.ForeignKey('page.PageVersion')
    content = models.ForeignKey('page.PageContent')
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment')
    priority = models.IntegerField()
