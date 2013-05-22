from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200)

class Site(models.Model):
    domain = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    template = models.ForeignKey('core.SiteTemplate')

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
    code = models.CharField(max_length=2) # Corresponds to ISO 3166-2:NO (https://no.wikipedia.org/wiki/ISO_3166-2:NO)
    name = models.CharField(max_length=100)

    @staticmethod
    def typical_objects():
        # Returns the most typical County objects (excludes 'Jan Mayen' and 'Kontinentalsokkelen')
        return County.objects.exclude(code__in=['22', '23'])

# The country codes from Focus were extracted and duplicated here.
class FocusCountry(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    scandinavian = models.BooleanField()

    @staticmethod
    def get_sorted():
        countries = FocusCountry.objects.all()
        return {
            'norway': countries.get(code='NO'),
            'scandinavia': countries.filter(scandinavian=True).exclude(code='NO'),
            'other': countries.filter(scandinavian=False)
        }
