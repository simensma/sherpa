from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from association.models import Association

class Profile(models.Model):
    PHONE_MAX_LENGTH = 20

    user = models.OneToOneField(User)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True, unique=True)
    password_restore_date = models.DateTimeField(null=True)
    associations = models.ManyToManyField('association.Association', related_name='users')
    # At some point, this model will be extended to contain member data, syncing with Focus.

    def all_associations(self):
        if self.user.has_perm('user.sherpa_admin'):
            return Association.objects.all()
        else:
            return self.user.associations.all()

    class Meta:
        permissions = [
            ("sherpa_admin", "Sherpa-administrator - global access"),
            ("sherpa", "Has general access to Sherpa"),
        ]
