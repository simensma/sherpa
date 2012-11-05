from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20)
    password_restore_key = models.CharField(max_length=settings.RESTORE_PASSWORD_KEY_LENGTH, null=True, unique=True)
    password_restore_date = models.DateTimeField(null=True)
    # At some point, this model will be extended to contain member data, syncing with Focus.
    # It will also be connected with:
    # - Djangos Group model
    # - Djangos permission system.
    # - "association.Association"

class Zipcode(models.Model):
    zipcode = models.CharField(max_length=4)
    area = models.CharField(max_length=255)
    city_code = models.CharField(max_length=4)
    city = models.CharField(max_length=100)

class County(models.Model):
    code = models.CharField(max_length=2)
    sherpa_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)

# The country codes from Focus were extracted and duplicated here.
class FocusCountry(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255)
    scandinavian = models.BooleanField()
