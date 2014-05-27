# encoding: utf-8
from django.contrib.gis.db import models

class Tag(models.Model):
    """
    Any model can have a M2M-relation to this table in order to connect "tags", which are keywords, or labels,
    that can later be used for searching, filtering in all kinds of use cases.
    Note that ghost tags may remain when all related objects are deleted - this is by design as these tags
    will still appear as suggestions in autocomplete lists.
    """
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.pk

class Site(models.Model):
    domain = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    TYPE_CHOICES = (
        ('forening', u'Foreningens hjemmeside - bør kun være én per forening'),
        ('hytte', u'En betjent hytte eid av foreningen med egen hjemmeside'),
        ('kampanje', u'En egen kampanjeside forvaltet av foreningen'),
    )
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    TEMPLATE_CHOICES = (
        ('main', 'DNTs nasjonale nettside'),
        ('small', 'Medlemsforening eller turgruppe med et lite nettsted'),
        ('large', 'Medlemsforening eller turgruppe med et stort nettsted'),
    )
    template = models.CharField(max_length=255, choices=TEMPLATE_CHOICES)

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.domain)

class Zipcode(models.Model):
    zipcode = models.CharField(max_length=4)
    area = models.CharField(max_length=255)
    city_code = models.CharField(max_length=4)
    city = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.pk

class ZipcodeState(models.Model):
    last_update = models.DateTimeField()

    def __unicode__(self):
        return u'%s (last_update: %s)' % (self.pk, self.last_update)

class County(models.Model):
    code = models.CharField(max_length=2) # Corresponds to ISO 3166-2:NO (https://no.wikipedia.org/wiki/ISO_3166-2:NO)
    name = models.CharField(max_length=100)
    area = models.FloatField(null=True)
    perimeter = models.FloatField(null=True)
    geom = models.MultiPolygonField(null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return (u'%s: %s' % (self.pk, self.name)).encode('utf-8')

    @staticmethod
    def typical_objects():
        """
        Returns the most typical County objects (excludes 'Jan Mayen' and 'Kontinentalsokkelen')
        """
        return County.objects.exclude(code__in=['22', '23'])

class Municipality(models.Model):
    code = models.CharField(max_length=4) # Kommunenummer
    name = models.CharField(max_length=255)
    area = models.FloatField(null=True)
    perimeter = models.FloatField(null=True)
    geom = models.MultiPolygonField()
    # update_date is imported from a field called 'oppdatdato'. Specified for 56 out of 435 municipalities.
    # Not exactly sure what it is, but seems to be related to when the municipality was latest merged with
    # another municipality or changed somehow.
    update_date = models.DateTimeField(null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

# The country codes from Focus were extracted and duplicated here.
class FocusCountry(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    scandinavian = models.BooleanField()

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

    @staticmethod
    def get_sorted():
        countries = FocusCountry.objects.all()
        return {
            'norway': countries.get(code='NO'),
            'scandinavia': countries.filter(scandinavian=True).exclude(code='NO'),
            'other': countries.filter(scandinavian=False)
        }
