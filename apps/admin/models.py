from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings

import simples3

class Image(models.Model):
    key = models.CharField(max_length=8)
    extension = models.CharField(max_length=4)
    hash = models.CharField(max_length=40)
    description = models.TextField()
    album = models.ForeignKey('admin.Album', null=True)
    photographer = models.CharField(max_length=200)
    credits = models.CharField(max_length=200)
    licence = models.CharField(max_length=200)
    exif = models.TextField()
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('user.Profile')
    width = models.IntegerField()
    height = models.IntegerField()
    tags = models.ManyToManyField('core.Tag', related_name='images')

class ImageRecovery(models.Model):
    key = models.CharField(max_length=8)
    extension = models.CharField(max_length=4)
    hash = models.CharField(max_length=40)
    description = models.TextField()
    album = models.ForeignKey('admin.Album', null=True)
    photographer = models.CharField(max_length=200)
    credits = models.CharField(max_length=200)
    licence = models.CharField(max_length=200)
    exif = models.TextField()
    uploaded = models.DateTimeField(auto_now_add=True)
    width = models.IntegerField()
    height = models.IntegerField()
    tags = models.ManyToManyField('core.Tag', related_name='+')

# Upon image delete, delete the corresponding object from S3
@receiver(post_delete, sender=Image, dispatch_uid="admin.models")
def delete_image_post(sender, **kwargs):
    s3 = simples3.S3Bucket(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY, 'https://%s' % settings.AWS_BUCKET)

    s3.delete("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, kwargs['instance'].key, kwargs['instance'].extension))
    for size in settings.THUMB_SIZES:
        s3.delete("%s%s-%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, kwargs['instance'].key, str(size), kwargs['instance'].extension))

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)

    def __unicode__(self):
        return self.name

    def children(self):
        return Album.objects.filter(parent=self)

# Upon album delete, delete all child albums and connected images
@receiver(post_delete, sender=Album, dispatch_uid="admin.models")
def delete_album(sender, **kwargs):
    Album.objects.filter(parent=kwargs['instance']).delete()
    Image.objects.filter(album=kwargs['instance']).delete()
