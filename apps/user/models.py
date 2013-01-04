from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache

from focus.models import Actor

class Profile(models.Model):
    user = models.OneToOneField(User)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True, unique=True)
    password_restore_date = models.DateTimeField(null=True)
    associations = models.ManyToManyField('association.Association', related_name='users', through='AssociationRole')
    memberid = models.IntegerField(null=True, unique=True)
    sherpa_email = models.EmailField()

    ### Focus-related ###

    # Return this users' Actor (cached), or None
    def actor(self):
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
            return self.actor().first_name

    def get_last_name(self):
        if self.memberid is None:
            return self.user.last_name
        else:
            return self.actor().last_name

    def get_full_name(self):
        if self.memberid is None:
            return self.user.get_full_name()
        else:
            return "%s %s" % (self.actor().first_name, self.actor().last_name)

    def get_email(self):
        if self.memberid is None:
            return self.user.email
        else:
            return self.actor().email

    def get_sherpa_email(self):
        if self.sherpa_email != '':
            return self.sherpa_email
        else:
            return self.get_email()

    # Returns associations this user hs access to based on permissions
    def all_associations(self, role=None):
        from association.models import Association
        if self.user.has_perm('user.sherpa_admin'):
            if not role or role == 'admin':
                return Association.objects.all()
            else:
                return Association.objects.none()
        else:
            if role:
                return self.associations.filter(associationrole__role=role)
            else:
                return self.associations.all()

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
        # This is very silly, must be a better way to do this!?
        for choice in AssociationRole.ROLE_CHOICES:
            if choice[0] == role:
                return choice[1]
        return ''
