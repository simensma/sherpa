# encoding: utf-8
from django.db import models

from sherpa2.models import Forening as Sherpa2Forening

# Sometimes we'll need to reference foreninger directly by ID. We'll store the IDs we know and need here.
DNT_OSLO_ID = 2
DNT_UNG_OSLO_ID = 152

class Forening(models.Model):
    TYPES = [
        (u'sentral', u'Sentral/nasjonal'), # Sentral/nasjonal side - DNT Sentralt, DNT Ung, DNT Fjellsport
        (u'forening', u'Medlemsforening'), # Medlemsforeninger
        (u'turlag', u'Lokalt turlag'),     # Turlag, parent er forening
        (u'turgruppe', u'Turgruppe')]      # Turgruppe (har ikke medlemmer). Parent er forening _eller_ turlag

    # Applies only to 'turgruppe'-types
    GROUP_TYPES = [
        (u'barn', u'Barnas Turlag'),
        (u'ung', u'Ungdom'),
        (u'fjellsport', u'DNT Fjellsport'),
        (u'senior', u'DNT Senior')]

    name = models.CharField(max_length=255)
    parent = models.ForeignKey('foreninger.Forening', null=True, related_name='children')
    focus_id = models.IntegerField(null=True, default=None)
    type = models.CharField(max_length=255, choices=TYPES)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPES, default='')
    site = models.OneToOneField('core.Site', null=True)

    # Address
    post_address = models.CharField(max_length=255, default='')
    visit_address = models.CharField(max_length=255, default='')
    zipcode = models.ForeignKey('core.Zipcode', null=True)
    counties = models.ManyToManyField('core.County', related_name='foreninger')

    # Contact information
    phone = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    organization_no = models.CharField(max_length=255, default='')
    gmap_url = models.CharField(max_length=2048, default='') # Temporary - find other ways to display this map!
    facebook_url = models.CharField(max_length=2048, default='')

    def __unicode__(self):
        return u'%s: %s' % (self.pk, self.name)

    def get_with_children(self):
        foreninger = [self]
        for children in self.children.all():
            foreninger += children.get_with_children()
        return foreninger

    def get_main_forening(self):
        if self.type == 'sentral' or self.type == 'forening':
            return self
        else:
            return self.parent.get_main_forening()

    def get_old_url(self):
        """Temporary method! Retrieves the site URL from sherpa2"""
        try:
            return Sherpa2Forening.objects.get(id=self.id).url
        except Sherpa2Forening.DoesNotExist:
            return ''

    @staticmethod
    def sort(foreninger):
        foreninger = sorted(foreninger, key=lambda f: f.name.lower())
        return {
            'central': [f for f in foreninger if f.type == 'sentral'],
            'foreninger': [f for f in foreninger if f.type == 'forening'],
            'turlag': [f for f in foreninger if f.type == 'turlag'],
            'turgrupper': [f for f in foreninger if f.type == 'turgruppe'],
        }
