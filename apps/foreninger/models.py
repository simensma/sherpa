# encoding: utf-8
from django.db import models
from django.core.cache import cache
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .exceptions import ForeningTypeCannotHaveChildren, ForeningTypeNeedsParent, ForeningWithItselfAsParent, SentralForeningWithRelation, ForeningWithForeningParent, ForeningWithTurlagParent, TurlagWithTurgruppeParent, TurgruppeWithTurgruppeParent, ForeningParentIsChild, TurlagWithTurlagParent
from sherpa2.models import Forening as Sherpa2Forening
from sherpa2.models import NtbId
from core.models import Site

class Forening(models.Model):
    TYPES = [
        (u'sentral', u'Sentral/nasjonal'), # Central/national - only a handful; DNT, DNT ung, DNT Fjellsport
        (u'forening', u'Medlemsforening'), # Member associations (foreninger)
        (u'turlag', u'Lokalt turlag'),     # Local groups, must belong to a member association
        (u'turgruppe', u'Turgruppe'),      # Tourgroup (has no members), must belong to a member association OR local group
    ]

    # Applies only to 'turgruppe'-types
    GROUP_TYPES = [
        (u'barn', u'Barnas Turlag'),
        (u'ung', u'Ungdom'),
        (u'fjellsport', u'DNT Fjellsport'),
        (u'senior', u'DNT Senior'),
        (u'other', u'Andre turgrupper'),
    ]

    name = models.CharField(max_length=255)
    # The child/parent rules are dependent on type; this is defined in admin.forening.forms.ExistingForeningDataForm
    parents = models.ManyToManyField('foreninger.Forening', related_name='children')
    focus_id = models.IntegerField(null=True, default=None)
    type = models.CharField(max_length=255, choices=TYPES)
    group_type = models.CharField(max_length=255, choices=GROUP_TYPES, default='')

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

    # The corresponding object ID in Nasjonal Turbase
    turbase_object_id = models.CharField(max_length=24, null=True)

    # Sometimes we'll need to reference foreninger directly by ID. We'll store a couple of IDs here.
    DNT_CENTRAL_ID = 56
    DNT_FJELLSPORT_ID =60
    DNT_UNG_ID = 1180
    DNT_OSLO_ID = 2
    DNT_UNG_OSLO_ID = 152

    # Public categories and their order
    PUBLIC_CATEGORIES = [
        (u'foreninger', u'Turistforeninger/turlag'),
        (u'barn', u'Barnas Turlag'),
        (u'ung', u'DNT ung'),
        (u'fjellsport', u'DNT fjellsport'),
        (u'senior', u'DNT senior'),
    ]

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '%s: %s' % (self.pk, self.name.encode('utf-8'))

    def get_sentral_name(self):
        """Some of the sentrale foreninger need to be displayed explicitly as sentrale in some cases. These are
        hardcoded for convenience at the moment, we might consider to reimplement this as a field on the forening-form
        applicable only for sentrale foreninger."""
        if self.id == Forening.DNT_CENTRAL_ID:
            return u'DNT sentralt'
        elif self.id == Forening.DNT_FJELLSPORT_ID:
            return u'DNT fjellsport sentralt'
        elif self.id == Forening.DNT_UNG_ID:
            return u'DNT ung sentralt'
        else:
            return self.name

    def get_parents_deep(self):
        parents = []
        for parent in self.parents.all():
            parents += parent.get_with_parents_deep()
        return parents

    def get_with_parents_deep(self):
        return [self] + self.get_parents_deep()

    def get_children_sorted(self):
        """Get children foreninger, sorted by type in form of a dict"""
        return Forening.sort(self.children.all())

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
            group_type[0]: [group for group in turgrupper if group.group_type == group_type[0]]
            for group_type in Forening.GROUP_TYPES
        }

    def get_main_foreninger(self):
        mains = cache.get('forening.main_foreninger.%s' % self.id)
        if mains is None:
            if self.type == 'sentral' or self.type == 'forening':
                mains = [self]
            else:
                mains = []
                for parent in self.parents.all():
                    mains += parent.get_main_foreninger()
            cache.set('forening.main_foreninger.%s' % self.id, mains, 60 * 60 * 24)
        return mains

    def get_active_domain(self):
        domain = self.get_active_url()[len('http://'):]
        domain.rstrip('/')
        return domain

    def get_active_url(self):
        """Returns the currently in-use URL for this forening. The homepage-site domain if the site is published,
        or the old sherpa2 URL if not."""
        homepage_site = self.get_homepage_site()
        if homepage_site is not None and homepage_site.is_published:
            return 'http://%s/' % homepage_site.domain
        else:
            return self.get_old_url()

    def get_old_url(self):
        """Temporary method! Retrieves the site URL from sherpa2"""
        old_url = cache.get('forening.old_sherpa2_url.%s' % self.id)
        if old_url is None:
            try:
                old_url = Sherpa2Forening.objects.get(id=self.id).url
            except Sherpa2Forening.DoesNotExist:
                old_url = ''
            cache.set('forening.old_sherpa2_url.%s' % self.id, old_url, 60 * 60 * 24)
        return old_url

    def get_homepage_site(self, prefetched=False):
        """A forening can have multiple related sites but only one homepage, this method returns the homepage site,
        or None if it doesn't have a homepage.
        If the prefetched parameter is set to True, we will assume that all related sites have been prefetched. To
        optimize for this, we won't filter the DB query on type but iterate all sites and programmatically filter out
        the homepage site (if any)."""
        # Use an empty list as sentinel value for no homepage site, since None is already used for cache miss
        NO_HOMEPAGE_SITE = []
        homepage_site = cache.get('forening.homepage_site.%s' % self.id)
        if homepage_site is None:
            try:
                if not prefetched:
                    # Default: perform a new DB filter query
                    homepage_site = self.sites.get(type='forening')
                else:
                    # If the data is prefetched, it'll be faster to iterate all() and filter programmatically
                    homepage_site = [site for site in self.sites.all() if site.type == 'forening'][0]
            except (Site.DoesNotExist, IndexError):
                homepage_site = NO_HOMEPAGE_SITE
            cache.set('forening.homepage_site.%s' % self.id, homepage_site, 60 * 60 * 24 * 7)
        if homepage_site == NO_HOMEPAGE_SITE:
            return None
        else:
            return homepage_site

    def get_homepage_site_prefetched(self):
        """Convenience method for templates"""
        return self.get_homepage_site(prefetched=True)

    def get_sites_sorted(self):
        return Site.sort(self.sites.all())

    def get_sites_sorted_by_type(self):
        return Site.sort_by_type(self.sites.all())

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

    @staticmethod
    def get_all_sorted():
        foreninger_sorted = cache.get('foreninger.all.sorted_by_type')
        if foreninger_sorted is None:
            foreninger_sorted = Forening.sort(Forening.objects.all())
            cache.set('foreninger.all.sorted_by_type', foreninger_sorted, 60 * 60 * 24 * 7)
        return foreninger_sorted

    @staticmethod
    def sort(foreninger):
        foreninger = sorted(foreninger, key=lambda f: f.name.lower())
        return {
            'sentral': [f for f in foreninger if f.type == 'sentral'],
            'forening': [f for f in foreninger if f.type == 'forening'],
            'turlag': [f for f in foreninger if f.type == 'turlag'],
            'turgruppe': [f for f in foreninger if f.type == 'turgruppe'],
        }

    @staticmethod
    def get_all_sorted_with_type_data():
        foreninger_sorted = cache.get('foreninger.all.sorted_by_type_with_type_data')
        if foreninger_sorted is None:
            foreninger_sorted = Forening.sort_with_type_data(Forening.objects.all())
            cache.set('foreninger.all.sorted_by_type_with_type_data', foreninger_sorted, 60 * 60 * 24 * 7)
        return foreninger_sorted

    @staticmethod
    def sort_with_type_data(foreninger):
        """Like sort(), but with both the code and name for each type. Preferably all use of sort() should
        be rewritten to replace it with this method."""
        foreninger = sorted(foreninger, key=lambda f: f.name.lower())
        return [{
            'code': type[0],
            'name': type[1],
            'foreninger': [f for f in foreninger if f.type == type[0]],
        } for type in Forening.TYPES]

    class Meta:
        ordering = ['name']

@receiver(pre_save, sender=Forening, dispatch_uid="foreninger.models")
def validate_forening_save(sender, **kwargs):
    # The following call will raise bubbled exception on error. It would have been the view's responsibility
    # to avoid this error before saving (like a db-enforced DatabaseError)
    kwargs['instance'].validate_relationships()
