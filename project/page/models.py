from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page')
    position = models.IntegerField()

class Page(models.Model):
    slug = models.CharField(max_length=50)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    # The active field can be set by the view in order to get a reference to
    # the active page version in the template. Not sure if there exists a better
    # way to do this?
    active = None

class PageVariant(models.Model):
    page = models.ForeignKey('page.Page')
    version = models.IntegerField()
    active = models.BooleanField()
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment', unique=True)
    # priority
    # probability
    # publisher = models.ForeignKey('auth.Profile')
    # change_comment = models.TextField()
    content = models.ForeignKey('page.PageContent', unique=True)

class PageContent(models.Model):
    content = models.TextField()
