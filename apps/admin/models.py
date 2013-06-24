from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings

import simples3

from page.models import *
from core.util import use_image_thumb

class Image(models.Model):
    key = models.CharField(max_length=8)
    extension = models.CharField(max_length=4)
    hash = models.CharField(max_length=40)
    description = models.TextField()
    album = models.ForeignKey('admin.Album', null=True)
    photographer = models.CharField(max_length=255)
    credits = models.CharField(max_length=255)
    licence = models.CharField(max_length=1023)
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

    def site_usage(self):
        return Content.objects.filter(type='image', content__icontains='%s.%s' % (self.key, self.extension), column__row__version__variant__page__isnull=False)

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

class Publication(models.Model):
    association = models.ForeignKey('association.Association')
    title = models.CharField(max_length=255)
    description = models.TextField()
    ACCESS_CHOICES = (
        ('all', 'Alle medlemmer'),
        ('association', 'Medlemmer i foreningen eller underforeninger'),)
    access = models.CharField(max_length=255, choices=ACCESS_CHOICES, default=ACCESS_CHOICES[0][0])
    LICENSE_CHOICES = (
        ('all_rights_reserved', 'Alle rettigheter reservert'),
        ('cc-by-nc-nd', 'Creative Commons Navngivelse-Ikkekommersiell-IngenBearbeidelse 3.0'),)
    license = models.CharField(max_length=255, choices=LICENSE_CHOICES, default=LICENSE_CHOICES[0][0])

    def releases_ordered(self):
        return self.releases.all().order_by('-pub_date')

    def released_releases_ordered(self):
        return [r for r in self.releases_ordered() if r.is_released()]

    def get_latest_release(self):
        try:
            return self.releases_ordered()[0]
        except IndexError:
            return ''

    def get_latest_cover_photo(self):
        try:
            return self.releases_ordered()[0].get_cover_photo()
        except IndexError:
            return ''

class Release(models.Model):
    publication = models.ForeignKey(Publication, related_name='releases')
    title = models.CharField(max_length=255)
    cover_photo = models.CharField(max_length=2048)
    description = models.TextField()
    pdf_hash = models.CharField(max_length=40)
    pdf_file_size = models.IntegerField(null=True, default=None)
    online_view = models.CharField(max_length=2048)
    pub_date = models.DateTimeField()
    tags = models.ManyToManyField('core.Tag', related_name='releases')

    def get_cover_photo(self):
        return use_image_thumb(self.cover_photo, 500)

    def get_pdf_url(self):
        return "http://%s/%s/%s.pdf" % (settings.AWS_BUCKET, settings.AWS_PUBLICATIONS_PREFIX, self.pdf_hash)

    def get_default_release(self):
        if self.pdf_hash != '':
            return self.get_pdf_url()
        elif self.online_view != '':
            return self.online_view
        else:
            return ''

    def get_default_release_type(self):
        if self.pdf_hash != '':
            return 'pdf'
        elif self.online_view != '':
            return 'online_view'
        else:
            return ''

    def is_released(self):
        return self.pdf_hash != '' or self.online_view != ''

# Upon image delete, delete the corresponding object from S3
@receiver(post_delete, sender=Release, dispatch_uid="admin.models")
def delete_release_pdf(sender, **kwargs):
    s3 = simples3.S3Bucket(
        settings.AWS_BUCKET,
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY,
        'https://%s' % settings.AWS_BUCKET)

    if kwargs['instance'].pdf_hash != '':
        s3.delete("%s/%s.pdf" % (settings.AWS_PUBLICATIONS_PREFIX, kwargs['instance'].pdf_hash))
