from django.db import models

class Page(models.Model):
    slug = models.CharField(max_length=50)
    published = models.BooleanField()

class PageVersion(models.Model):
    page = models.ForeignKey('page.Page')
    content = models.ForeignKey('page.PageContent')
    version = models.IntegerField()
    active = models.BooleanField()

class PageContent(models.Model):
    content = models.TextField()
