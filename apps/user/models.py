from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.context_processors import PermWrapper

from focus.models import Actor
from association.models import Association

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

    # Returns associations this user has the given role on, and not any other ones
    # Note that this also takes permissions into account, e.g. sherpa admins will have
    # all associations for 'admin' and none for 'user'
    def associations_with_role(self, role):
        if self.user.has_perm('user.sherpa_admin'):
            if role == 'admin':
                # Sherpa admins are admins on all associations
                return Association.objects.all()
            else:
                # Sherpa admins are not any other role than admin on any associations
                return Association.objects.none()
        else:
            # Filter on the role we're looking for
            return self.associations.filter(associationrole__role=role)

    # Returns associations this user has access to.
    # Note that this also takes permissions into account, e.g. sherpa admins will
    # have access to all associations
    def all_associations(self):
        if self.user.has_perm('user.sherpa_admin'):
            # Sherpa admins have access to all associations
            return Association.objects.all()
        else:
            # A normal user, return all connected associations
            return self.associations.all()

    def all_associations_sorted(self):
        return Association.sort_and_apply_roles(self.all_associations(), self.user)

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
