from django.db import models

class SMSServiceRequest(models.Model):
    profile = models.ForeignKey('user.Profile', null=True) # Null if the user isn't authenticated
    user = models.ForeignKey('user.User', null=True) # Null if the user isn't authenticated
    ip = models.CharField(max_length=15)
    phone_number_input = models.CharField(max_length=255, null=True) # Null if the request came from Min side
    memberid = models.IntegerField(max_length=255, null=True) # Null if no match
    count = models.IntegerField() # The number of requests we've recorded from this user thus far
    blocked = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
