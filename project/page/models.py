from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page', unique=True)
    position = models.IntegerField(unique=True)

class Page(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)

class PageVariant(models.Model):
    page = models.ForeignKey('page.Page')
    slug = models.CharField(max_length=50, unique=True, null=True)
    segment = models.ForeignKey('analytics.Segment', null=True)
    # priority
    # probability
    # publisher = models.ForeignKey('auth.Profile')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

class PageVersion(models.Model):
    variant = models.ForeignKey('page.PageVariant')
    content = models.ForeignKey('page.PageContent', unique=True)
    version = models.IntegerField()
    active = models.BooleanField()

class PageContent(models.Model):
    content = models.TextField()
