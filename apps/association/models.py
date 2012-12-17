# encoding: utf-8
from django.db import models

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

    role = None # Can be set to contain a M2M-field for a user instance
    def apply_role(self, user):
        if user.has_perm('user.sherpa_admin'):
            self.role = 'admin'
        else:
            from user.models import AssociationRole
            self.role = AssociationRole.objects.get(profile=user.get_profile(), association=self).role

    @staticmethod
    def sort(associations):
        associations = associations.order_by('name')
        return {
            'central': associations.filter(type='sentral'),
            'associations': associations.filter(type='forening'),
            'small_associations': associations.filter(type='turlag'),
            'hike_groups': associations.filter(type='turgruppe'),
        }

    @staticmethod
    def sort_and_apply_roles(associations, user):
        associations = Association.sort(associations)
        for list in associations.values():
            for association in list:
                association.apply_role(user)
        return associations