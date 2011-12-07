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
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment', null=True)
    priority = models.IntegerField()
    # probability
    # publisher = models.ForeignKey('auth.Profile')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

class PageVersion(models.Model):
    variant = models.ForeignKey('page.PageVariant')
    version = models.IntegerField()
    active = models.BooleanField()

### Layouts

class Layout(models.Model):
    version = models.ForeignKey('page.PageVersion')
    template = models.CharField(max_length=50) # Actual template name? Or int? Just a unique ID
    order = models.IntegerField()
    columns = []

class HTMLContent(models.Model):
    layout = models.ForeignKey('page.Layout')
    content = models.TextField()
    column = models.IntegerField()
    order = models.IntegerField()

class Widget(models.Model):
    layout = models.ForeignKey('page.Layout')
    widget = models.TextField()
    column = models.IntegerField()
    order = models.IntegerField()
