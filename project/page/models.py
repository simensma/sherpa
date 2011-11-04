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

class PageVersion(models.Model):
    page = models.ForeignKey('page.Page')
    content = models.ForeignKey('page.PageContent')
    version = models.IntegerField()
    active = models.BooleanField()
    #publisher = models.ForeignKey('auth.Profile')
    #change_comment = models.TextField()

class PageContent(models.Model):
    content = models.TextField()
