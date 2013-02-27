from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.context_processors import PermWrapper

from focus.models import Actor
from association.models import Association

from itertools import groupby

class Profile(models.Model):
    user = models.OneToOneField(User)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True)
    password_restore_date = models.DateTimeField(null=True)
    associations = models.ManyToManyField('association.Association', related_name='users', through='AssociationRole')
    memberid = models.IntegerField(null=True, unique=True)
    sherpa_email = models.EmailField()

    # Shortcut for templates to get any user perms via Profile
    def perms(self):
        return PermWrapper(self.user)

    ### Focus-related ###

    # Return this users' Actor (cached), or None
    def get_actor(self):
        if self.memberid is None:
            return None
        actor = cache.get('actor.%s' % self.memberid)
        if actor is None:
            actor = Actor.objects.get(memberid=self.memberid)
            cache.set('actor.%s' % self.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)
        return actor

    def get_first_name(self):
        if self.memberid is None:
            return self.user.first_name
        else:
            return self.get_actor().first_name

    def get_last_name(self):
        if self.memberid is None:
            return self.user.last_name
        else:
            return self.get_actor().last_name

    def get_full_name(self):
        if self.memberid is None:
            return self.user.get_full_name()
        else:
            return "%s %s" % (self.get_actor().first_name, self.get_actor().last_name)

    def get_email(self):
        if self.memberid is None:
            return self.user.email
        else:
            return self.get_actor().email

    def get_sherpa_email(self):
        if self.sherpa_email != '':
            return self.sherpa_email
        else:
            return self.get_email()

    # Returns associations this user has access to.
    # Note that this also takes permissions into account, e.g. sherpa admins will
    # have access to all associations
    def all_associations(self):
        associations = cache.get('profile.%s.all_associations' % self.id)
        if associations is None:
            if self.user.has_perm('user.sherpa_admin'):
                # Sherpa admins have access to all associations
                associations = Association.objects.all()
            else:
                # A normal user, return all connected associations, including
                # children-associations where role is admin.
                associations = []
                for association in self.associations.all():
                    role = AssociationRole.objects.get(association=association, profile=self).role
                    if role == 'admin':
                        # Add this one and all its children
                        for association in association.get_with_children():
                            association.role = 'admin'
                            associations.append(association)
                    elif role == 'user':
                        # Just add this one
                        association.role = 'user'
                        associations.append(association)

                # Since this will add duplicates if any of the related associations
                # are child/parent-related with each other, remove the one with lowest role
                def pick_dupe(associations):
                    # This defines role priority
                    # Pick the dupe with role admin if existing, if not, just pick any dupe.
                    admins = [a for a in associations if a.role == 'admin']
                    if len(admins) > 0:
                        return admins[0]
                    else:
                        return associations[0]

                ## Sort and group by association id, and remove dupes
                sorted_associations = sorted(associations, key=lambda a: a.id)
                grouped_associations = groupby(sorted_associations, key=lambda a: a.id)
                associations = [pick_dupe(list(group)) for key, group in grouped_associations]
            cache.set('profile.%s.all_associations' % self.id, associations, 60 * 60 * 24)
        return associations

    def all_associations_sorted(self):
        return Association.sort(self.all_associations())

    class Meta:
        permissions = [
            ("sherpa_admin", "Sherpa-administrator - global access"),
            ("sherpa", "Has general access to Sherpa"),
        ]

class AssociationRole(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('user', 'Vanlig bruker'),)
    profile = models.ForeignKey('user.Profile')
    association = models.ForeignKey('association.Association')
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)

    @staticmethod
    def friendly_role(role):
        # Assumes that 'role' exists in the tuple and is unique
        return [c[1] for c in AssociationRole.ROLE_CHOICES if c[0] == role][0]
