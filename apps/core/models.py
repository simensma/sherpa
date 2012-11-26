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
    prefix = models.CharField(max_length=200)

class SiteTemplate(models.Model):
    name = models.CharField(max_length=100)

class Zipcode(models.Model):
    zipcode = models.CharField(max_length=4)
    area = models.CharField(max_length=255)
    city_code = models.CharField(max_length=4)
    city = models.CharField(max_length=100)

class ZipcodeState(models.Model):
    last_update = models.DateTimeField()

class County(models.Model):
    code = models.CharField(max_length=2)
    sherpa_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)

# The country codes from Focus were extracted and duplicated here.
class FocusCountry(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    scandinavian = models.BooleanField()
