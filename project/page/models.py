from django.db import models

class Page(models.Model):
    slug = models.CharField(max_length=50)
    published = models.BooleanField()
    # The active field can be set by the view in order to get a reference to
    # the active page version in the template. Not sure if there exists a better
    # way to do this?
    active = None

class PageVersion(models.Model):
    page = models.ForeignKey('page.Page')
    content = models.ForeignKey('page.PageContent')
    version = models.IntegerField()
    active = models.BooleanField()

class PageContent(models.Model):
    content = models.TextField()
