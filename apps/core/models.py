from django.db import models
from django.contrib.sites.models import Site

class Tag(models.Model):
    name = models.CharField(max_length=200)

class Search(models.Model):
    query = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)

class SiteDetails(models.Model):
    site = models.OneToOneField(Site, related_name='details')
    template = models.ForeignKey('core.SiteTemplate')

class SiteTemplate(models.Model):
    name = models.CharField(max_length=100)
