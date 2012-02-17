from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings
from lib import S3

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

# Upon image delete, delete the corresponding object from S3
@receiver(post_delete, sender=Image)
def delete_image(sender, **kwargs):
    conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + kwargs['instance'].key)
    conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + kwargs['instance'].key + "-500")
    conn.delete(settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX + kwargs['instance'].key + "-150")

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)
    # Todo: Author, or some other sort of affiliation?

# Upon album delete, delete all child albums and connected images
@receiver(post_delete, sender=Album)
def delete_album(sender, **kwargs):
    Album.objects.filter(parent=kwargs['instance']).delete()
    Image.objects.filter(album=kwargs['instance']).delete()

class Keyword(models.Model):
    image = models.ForeignKey('admin.Image')
    name = models.CharField(max_length=200)
