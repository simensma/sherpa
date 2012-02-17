from django.db import models
from lib import S3
from django.conf import settings

class Image(models.Model):
    key = models.CharField(max_length=8)
    hash = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    album = models.ForeignKey('admin.Album')
    credits = models.CharField(max_length=20)
    photographer = models.CharField(max_length=200)
    photographer_contact = models.CharField(max_length=200)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('user.Profile')
    width = models.IntegerField()
    height = models.IntegerField()

    def delete(self):
        conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + self.key)
        conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + self.key + "-500")
        conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + self.key + "-150")
        super(Image, self).delete()

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)
    # Todo: Author, or some other sort of affiliation?

class Keyword(models.Model):
    image = models.ForeignKey('admin.Image')
    name = models.CharField(max_length=200)
