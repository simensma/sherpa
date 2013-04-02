from django.db import models

class Aktivitet(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    tags = models.ManyToManyField('core.Tag', related_name='aktiviteter')
    participants = models.ManyToManyField('user.Profile', related_name='aktiviteter')
