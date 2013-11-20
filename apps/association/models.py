# encoding: utf-8
from django.db import models

# Sometimes we'll need to reference associations directly by ID. We'll store the IDs we know and need here.
dnt_oslo_id = 2
dnt_ung_oslo_id = 152

class Association(models.Model):
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
    parent = models.ForeignKey('association.Association', null=True, related_name='children')
    focus_id = models.IntegerField(null=True, default=None)
    type = models.CharField(max_length=255, choices=TYPES)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPES, default='')
    site = models.OneToOneField('core.Site', null=True)

    # Address
    post_address = models.CharField(max_length=255, default='')
    visit_address = models.CharField(max_length=255, default='')
    zipcode = models.ForeignKey('core.Zipcode', null=True)
    counties = models.ManyToManyField('core.County', related_name='associations')

    # Contact information
    phone = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    organization_no = models.CharField(max_length=255, default='')
    gmap_url = models.CharField(max_length=2048, default='') # Temporary - find other ways to display this map!
    facebook_url = models.CharField(max_length=2048, default='')

    def get_with_children(self):
        associations = [self]
        for children in self.children.all():
            associations += children.get_with_children()
        return associations

    def get_main_association(self):
        if self.type == 'sentral' or self.type == 'forening':
            return self
        else:
            return self.parent.get_main_association()

    @staticmethod
    def sort(associations):
        associations = sorted(associations, key=lambda a: a.name.lower())
        return {
            'central': [a for a in associations if a.type == 'sentral'],
            'associations': [a for a in associations if a.type == 'forening'],
            'small_associations': [a for a in associations if a.type == 'turlag'],
            'hike_groups': [a for a in associations if a.type == 'turgruppe'],
        }
