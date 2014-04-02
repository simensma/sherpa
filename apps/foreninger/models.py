# encoding: utf-8
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .exceptions import ForeningTypeCannotHaveChildren, ForeningTypeNeedsParent, ForeningWithItselfAsParent, SentralForeningWithRelation, ForeningWithForeningParent, ForeningWithTurlagParent, TurlagWithTurgruppeParent, TurgruppeWithTurgruppeParent, ForeningParentIsChild, TurlagWithTurlagParent
from sherpa2.models import Forening as Sherpa2Forening

# Sometimes we'll need to reference foreninger directly by ID. We'll store the IDs we know and need here.
DNT_OSLO_ID = 2
DNT_UNG_OSLO_ID = 152

class Forening(models.Model):
    TYPES = [
        (u'sentral', u'Sentral/nasjonal'), # Central/national - only a handful; DNT, DNT ung, DNT Fjellsport
        (u'forening', u'Medlemsforening'), # Member associations (foreninger)
        (u'turlag', u'Lokalt turlag'),     # Local groups, must belong to a member association
        (u'turgruppe', u'Turgruppe')]      # Tourgroup (has no members), must belong to a member association OR local group

    # Applies only to 'turgruppe'-types
    GROUP_TYPES = [
        (u'barn', u'Barnas Turlag'),
        (u'ung', u'Ungdom'),
        (u'fjellsport', u'DNT Fjellsport'),
        (u'senior', u'DNT Senior')]

    name = models.CharField(max_length=255)
    # The child/parent rules are dependent on type; this is defined in admin.forening.forms.ExistingForeningDataForm
    parents = models.ManyToManyField('foreninger.Forening', related_name='children')
    focus_id = models.IntegerField(null=True, default=None)
    type = models.CharField(max_length=255, choices=TYPES)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPES, default='')
    site = models.OneToOneField('core.Site', null=True)

    # Address
    post_address = models.CharField(max_length=255, default='')
    visit_address = models.CharField(max_length=255, default='')
    zipcode = models.ForeignKey('core.Zipcode', null=True)
    counties = models.ManyToManyField('core.County', related_name='foreninger')

    # Contact information - user may choose between setting the relation (which automatically fills name/phone/email,
    # manually providing a contact person (name/phone/email), or only setting phone/email
    contact_person = models.ForeignKey('user.User', null=True)
    contact_person_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    organization_no = models.CharField(max_length=255, default='')
    gmap_url = models.CharField(max_length=2048, default='') # Temporary - find other ways to display this map!
    facebook_url = models.CharField(max_length=2048, default='')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '%s: %s' % (self.pk, self.name.encode('utf-8'))

    def get_parents_deep(self):
        parents = []
        for parent in self.parents.all():
            parents += parent.get_with_parents_deep()
        return parents

    def get_with_parents_deep(self):
        return [self] + self.get_parents_deep()

    def get_children_sorted(self):
        """Get children foreninger, sorted by type in form of a dict"""
        children = self.children.all()
        return {
            'sentral': children.filter(type='sentral'),
            'forening': children.filter(type='forening'),
            'turlag': children.filter(type='turlag'),
            'turgruppe': children.filter(type='turgruppe'),
        }

    def get_with_children_deep(self):
        """Return a deep search of this forenings children and all their (deep-searched) children,
        including this forening itself."""
        return [self] + self.get_children_deep()

    def get_children_deep(self):
        """Return a deep search of this forenings children and all their (deep-searched) children."""
        foreninger = []
        for children in self.children.all():
            foreninger += children.get_with_children_deep()
        return foreninger

    def get_turgrupper_deep(self):
        """Return all turgrupper that are children of this, or of any children of this, forening"""
        turgrupper = []
        for child in self.children.all():
            if child.type == 'turgruppe':
                turgrupper.append(child)
            turgrupper += child.get_turgrupper_deep()
        return turgrupper

    def get_turgrupper_deep_sorted_by_group(self):
        turgrupper = sorted(self.get_turgrupper_deep(), key=lambda g: g.name)
        return {
            'barn': [g for g in turgrupper if g.group_type == 'barn'],
            'ung': [g for g in turgrupper if g.group_type == 'ung'],
            'fjellsport': [g for g in turgrupper if g.group_type == 'fjellsport'],
            'senior': [g for g in turgrupper if g.group_type == 'senior'],
        }

    def get_main_forenings(self):
        if self.type == 'sentral' or self.type == 'forening':
            return [self]
        else:
            mains = []
            for parent in self.parents.all():
                mains += parent.get_main_forenings()
            return mains

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

    def validate_relationships(self, simulate_type=None, simulate_parents=None):
        """Validate a forening's relationships based on its type and its relationships types
        See https://turistforeningen.atlassian.net/wiki/pages/viewpage.action?pageId=1540233"""

        # Callers may simulate the type and/or parents fields, e.g. for form validation purposes
        type = self.type if simulate_type is None else simulate_type
        if simulate_parents is not None:
            parents = simulate_parents
        elif self.id is None:
            parents = []
        else:
            parents = self.parents.all()

        # A central group cannot have any children
        if self.id is not None and type in ['sentral', 'turgruppe'] and self.children.count() > 0:
            raise ForeningTypeCannotHaveChildren()

        # These types must have a parent
        if self.id is not None and self.type in ['turlag', 'turgruppe'] and len(parents) == 0:
            raise ForeningTypeNeedsParent()

        # Parent-related validations
        for parent in parents:

            if self == parent:
                raise ForeningWithItselfAsParent()

            # Central foreninger can't have relationships
            if type == 'sentral' or parent.type == 'sentral':
                raise SentralForeningWithRelation()

            # Forening can't be child of other forening
            if type == 'forening' and parent.type == 'forening':
                raise ForeningWithForeningParent()

            # Turlag can't be child of other turlag
            if type == 'turlag' and parent.type == 'turlag':
                raise TurlagWithTurlagParent()

            # Turgruppe can't be child of other turgruppe
            if type == 'turgruppe' and parent.type == 'turgruppe':
                raise TurgruppeWithTurgruppeParent()

            # Forening can't be child of turlag/turgruppe
            if type == 'forening' and parent.type in ['turlag', 'turgruppe']:
                raise ForeningWithTurlagParent()

            # Turlag can't be child of turgruppe
            if type == 'turlag' and parent.type == 'turgruppe':
                raise TurlagWithTurgruppeParent()

            # The parent can't already be a child - this would probably be impossible due to above
            # rules, but check explicitly anyway
            if self.id is not None and parent in self.get_children_deep():
                exc = ForeningParentIsChild()
                exc.parent = parent
                raise exc

    class Meta:
        ordering = ['name']

@receiver(pre_save, sender=Forening, dispatch_uid="foreninger.models")
def validate_forening_save(sender, **kwargs):
    # The following call will raise bubbled exception on error. It would have been the view's responsibility
    # to avoid this error before saving (like a db-enforced DatabaseError)
    kwargs['instance'].validate_relationships()
