from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache

from focus.models import Actor

class Profile(models.Model):
    PHONE_MAX_LENGTH = 20

    user = models.OneToOneField(User)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True, unique=True)
    password_restore_date = models.DateTimeField(null=True)
    associations = models.ManyToManyField('association.Association', related_name='users', through='AssociationRole')
    memberid = models.IntegerField(null=True, unique=True)

    # Focus-related
    def actor(self):
        if self.memberid is None:
            return None
        actor = cache.get('actor.%s' % self.memberid)
        if actor is None:
            actor = Actor.objects.get(memberid=self.memberid)
            cache.set('actor.%s' % self.memberid, actor, 60 * 60)
        return actor

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
