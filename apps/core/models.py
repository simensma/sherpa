from django.contrib.gis.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.pk

class Site(models.Model):
    domain = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    template = models.ForeignKey('core.SiteTemplate')

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.domain)

class SiteTemplate(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

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
        return u'%s: %s' % (self.pk, self.name)

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
