# encoding: utf-8
from datetime import datetime, date

from django.contrib.gis.db import models

from admin.models import Campaign
from articles.models import Article
from page.models import Menu, Page, AdPlacement

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
        ('forening', u'Foreningens hjemmeside'), # Zero or one per forening
        ('hytte', u'Hjemmeside for en betjent hytte'),
        ('kampanje', u'Kampanjeside'),
    )
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    TEMPLATE_CHOICES = (
        ('central', 'DNTs nasjonale nettsted'),
        ('local', 'Medlemsforening eller turgruppe sitt nettsted'),
    )
    template = models.CharField(max_length=255, choices=TEMPLATE_CHOICES)
    forening = models.ForeignKey('foreninger.Forening', related_name='sites')
    title = models.CharField(max_length=255) # Only specified for type='kampanje', empty and unused for other types
    analytics_ua = models.CharField(max_length=255, null=True)

    # Most sites should be published, but when new sites are created this can be set to False and a few things will
    # change accordingly; a warning label will be shown on all pages and foreninger will refer to the old sherpa2 URL
    # as its homepage instead of the site domain (the latter applies only for type='forening').
    is_published = models.BooleanField(default=False)

    # Hardcoded site IDs that we may need to know
    DNT_CENTRAL_ID = 1

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.domain)

    def get_type(self):
        return [t for t in Site.TYPE_CHOICES if t[0] == self.type][0][1]

    def get_type_short(self):
        """Return an even shorter friendly name than the TYPE_CHOICES tuple description"""
        if self.type == 'forening':
            return "Hjemmeside"
        elif self.type == 'hytte':
            return "Hytteside"
        elif self.type == 'kampanje':
            return "Kampanjeside"
        else:
            raise Exception("Unrecognized site type '%s'" % self.type)

    def get_title(self):
        """Return the site title based on what type the site is"""
        if self.type == 'forening':
            return self.forening.name
        elif self.type == 'hytte':
            # TODO: We should fetch this automatically when the site is connected to a cabin.
            # At that point, clear the title field for all hytte-sites and remove the option to
            # input title for hytte-site when creating new sites.
            return self.title
        elif self.type == 'kampanje':
            return self.title
        else:
            raise Exception("Unrecognized site type '%s'" % self.type)

    def get_page_count(self):
        return Page.on(self).filter(
            pub_date__lte=datetime.now(),
            published=True,
        ).count()

    def get_news_count(self):
        return Article.on(self).filter(
            pub_date__lte=datetime.now(),
            published=True,
        ).count()

    def get_menu_count(self):
        return Menu.on(self).count()

    def get_campaign_count(self):
        return Campaign.on(self).count()

    def get_ad_count(self):
        today = date.today()
        return AdPlacement.on(self).filter(
            start_date__lte=today,
            end_date__gte=today,
        ).count()

    @staticmethod
    def sort(sites):
        """Sort the given sites iterable by title and return a dict with a key for each site type, containing
        a list of sites of that type"""
        sites = sorted(sites, key=lambda s: s.get_title())
        types = [t[0] for t in Site.TYPE_CHOICES]
        return {t: [s for s in sites if s.type == t] for t in types}

    @staticmethod
    def sort_by_type(sites):
        """Sort the given sites iterable by (type, title) return the result as a flat list"""
        sites_by_title = sorted(sites, key=lambda s: s.get_title())
        sites_by_type = []
        for type in Site.TYPE_CHOICES:
            for site in sites_by_title:
                if site.type == type[0]:
                    sites_by_type.append(site)
        return sites_by_type

    @staticmethod
    def verify_domain(domain):
        """Very simple syntax verification, and a few business rules"""
        domain = domain.strip()
        if domain == '' or not '.' in domain:
            return {
                'valid': False,
                'error': 'malformed',
            }

        if domain.endswith('/'):
            domain = domain[:-1]

        if '/' not in domain:
            prefix = ''
        else:
            try:
                # Prefix folder specified
                domain, prefix = domain.split('/')
                # Only allowed for turistforeningen.no
                if domain != 'turistforeningen.no' and domain != 'www.turistforeningen.no':
                    return {
                        'valid': False,
                        'error': 'prefix_for_disallowed_domain',
                    }
            except ValueError:
                # More than one subdir specified
                return {
                    'valid': False,
                    'error': 'more_than_one_subdir',
                }

        if prefix != '':
            return {
                'valid': False,
                'error': 'prefix_not_supported_yet',
            }

        if not domain.endswith('.test.turistforeningen.no'):
            return {
                'valid': False,
                'error': 'test_period_requires_test_domain',
            }

        if domain.count('.') == 1 and not domain.startswith('www'):
            domain = "www.%s" % domain

        try:
            existing_site = Site.objects.get(domain=domain, prefix=prefix)
            existing_forening = existing_site.forening
            return {
                'valid': False,
                'error': 'site_exists',
                'existing_forening': existing_forening,
            }
        except Site.DoesNotExist:
            pass

        return {
            'valid': True,
            'domain': domain,
            'prefix': prefix,
        }

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
