# encoding: utf-8
from datetime import date
import json
import random

from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings

import boto

from core.util import use_image_thumb, s3_bucket

class Image(models.Model):
    key = models.CharField(max_length=8)
    extension = models.CharField(max_length=4)
    hash = models.CharField(max_length=40)
    description = models.TextField()
    album = models.ForeignKey('admin.Album', null=True, related_name='images')
    photographer = models.CharField(max_length=255)
    credits = models.CharField(max_length=255)
    licence = models.CharField(max_length=1023)
    exif = models.TextField()
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('user.User', null=True)
    width = models.IntegerField()
    height = models.IntegerField()
    tags = models.ManyToManyField('core.Tag', related_name='images')

    def get_url(self):
        return '//%s/%s%s.%s' % (s3_bucket(), settings.AWS_IMAGEGALLERY_PREFIX, self.key, self.extension)

    @staticmethod
    def generate_random_key():
        def random_alphanumeric():
            # These "magic" numbers generate one of [a-zA-Z0-9] based on the ascii table.
            r = random.randint(0, 61)
            if  (r < 10): return chr(r + 48)
            elif(r < 36): return chr(r + 55)
            else        : return chr(r + 61)
        return "%s%s/%s%s/%s%s" % (random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric(), random_alphanumeric())

    @staticmethod
    def generate_unique_random_key():
        key = Image.generate_random_key()
        while Image.objects.filter(key=key).exists():
            # Potential weak spot here if the amount of objects
            # were to close in on the amount of available keys.
            key = Image.generate_random_key()
        return key

    def __unicode__(self):
        return u'%s' % self.pk

# Upon image delete, delete the corresponding object from S3
@receiver(post_delete, sender=Image, dispatch_uid="admin.models")
def delete_image_post(sender, **kwargs):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    bucket.delete_key("%s%s.%s" % (
        settings.AWS_IMAGEGALLERY_PREFIX,
        kwargs['instance'].key,
        kwargs['instance'].extension
    ))
    for size in settings.THUMB_SIZES:
        bucket.delete_key("%s%s-%s.%s" % (
            settings.AWS_IMAGEGALLERY_PREFIX,
            kwargs['instance'].key,
            str(size),
            kwargs['instance'].extension
        ))

class Album(models.Model):
    # Static Album ID reference for images from imported aktiviteter
    IMPORTED_AKTIVITETER_ALBUM_ID = 66

    # The number of images to split album downloads into
    DOWNLOAD_PART_COUNT = 150

    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.pk, self.name)

    def children(self):
        return Album.objects.filter(parent=self)

# Upon album delete, delete all child albums and connected images
@receiver(post_delete, sender=Album, dispatch_uid="admin.models")
def delete_album(sender, **kwargs):
    Album.objects.filter(parent=kwargs['instance']).delete()
    Image.objects.filter(album=kwargs['instance']).delete()

class Fotokonkurranse(models.Model):
    album = models.ForeignKey(Album, null=True)

class Publication(models.Model):
    forening = models.ForeignKey('foreninger.Forening')
    title = models.CharField(max_length=255)
    description = models.TextField()
    ACCESS_CHOICES = (
        ('all', 'Alle medlemmer'),
        ('forening', 'Medlemmer i foreningen eller underforeninger'),)
    access = models.CharField(max_length=255, choices=ACCESS_CHOICES, default=ACCESS_CHOICES[0][0])
    LICENSE_CHOICES = (
        ('all_rights_reserved', 'Alle rettigheter reservert'),
        ('cc-by-nc-nd', 'Creative Commons Navngivelse-Ikkekommersiell-IngenBearbeidelse 3.0'),)
    license = models.CharField(max_length=255, choices=LICENSE_CHOICES, default=LICENSE_CHOICES[0][0])

    def __unicode__(self):
        return u'%s (%s)' % (self.pk, self.title)

    def releases_ordered(self):
        return self.releases.all().order_by('-pub_date')

    def released_releases_ordered(self):
        return [r for r in self.releases.filter(pub_date__lte=date.today()).order_by('-pub_date') if r.is_available()]

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

    def __unicode__(self):
        return u'%s (%s)' % (self.pk, self.title)

    def get_cover_photo(self):
        return use_image_thumb(self.cover_photo, 500)

    def get_pdf_url(self):
        return "http://%s/%s/%s.pdf" % (s3_bucket(), settings.AWS_PUBLICATIONS_PREFIX, self.pdf_hash)

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

    def is_available(self):
        return self.pdf_hash != '' or self.online_view != ''

# Upon image delete, delete the corresponding object from S3
@receiver(post_delete, sender=Release, dispatch_uid="admin.models")
def delete_release_pdf(sender, **kwargs):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    if kwargs['instance'].pdf_hash != '':
        bucket.delete_key("%s/%s.pdf" % (settings.AWS_PUBLICATIONS_PREFIX, kwargs['instance'].pdf_hash))

class Campaign(models.Model):
    title = models.CharField(max_length=255)

    # On Campaign creation, we'll generate a Google Analytics event label which cannot change
    ga_event_label = models.CharField(max_length=255)

    # UTM campaign name is saved because it can't be changed after the first save
    utm_campaign = models.CharField(max_length=255)

    image_original = models.CharField(max_length=2048) # URL to the original image, anywhere on the interweb
    image_cropped_hash = models.CharField(max_length=255) # Hash of the same image, cropped/resized and saved on our S3

    # image_crop is in JSON format and contains the following:
    # selection: {
    #   x: left coordinate
    #   x2: right coordinate
    #   y: top coordinate
    #   y2: bottom coordinate
    #   w: total width of cropped area (x2 - x)
    #   h: total height of cropped area (y2 - y)
    # }
    # width: the total width of the image dimension in which the cropping selection was made
    # height: cropped total height (like width)
    #
    # Note that:
    # - selection is in the Jcrop format: http://www.deepliquid.com/content/Jcrop_Manual.html
    # - width and height is NOT necessarily the full size of the image
    image_crop = models.CharField(max_length=1024)

    photographer = models.CharField(max_length=255)
    PHOTOGRAPHER_ALIGNMENT_CHOICES = (
        (u'left', u'Venstre'),
        (u'right', u'Høyre'),
    )
    photographer_alignment = models.CharField(max_length=10, choices=PHOTOGRAPHER_ALIGNMENT_CHOICES)
    PHOTOGRAPHER_COLOR_CHOICES = (
        (u'white', u'Hvit'),
        (u'black', u'Sort'),
    )
    photographer_color = models.CharField(max_length=10, choices=PHOTOGRAPHER_COLOR_CHOICES)
    button_enabled = models.BooleanField()
    button_label = models.CharField(max_length=1024)
    button_anchor = models.CharField(max_length=2048)
    button_large = models.BooleanField()
    button_position = models.CharField(max_length=512) # JSON

    created = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey('core.Site')

    def to_json(self):
        return json.dumps({
            'image_original': self.image_original,
            'image_crop': json.loads(self.image_crop),
            'photographer': self.photographer,
            'photographer_alignment': self.photographer_alignment,
            'photographer_color': self.photographer_color,
            'button_enabled': self.button_enabled,
            'button_label': self.button_label,
            'button_anchor': self.button_anchor,
            'button_large': self.button_large,
            'button_position': json.loads(self.button_position),
            'text': [{
                'content': t.content,
                'style': json.loads(t.style),
            } for t in self.text.all()],
        })

    def render_button_style(self):
        style_string = ''
        for item, value in json.loads(self.button_position).items():
            style_string += '%s:%s;' % (item, value)
        return style_string

    def get_button_anchor(self):
        """Returns the button anchor with utm campaign parameters"""
        if '?' not in self.button_anchor:
            start_char = '?'
        else:
            start_char = '&'
        return '%s%sutm_campaign=%s&utm_source=kampanje&utm_medium=kampanjeknapp' % (self.button_anchor, start_char, self.utm_campaign)

    def get_cropped_image(self):
        return "http://%s/%s" % (s3_bucket(), self.get_cropped_image_key())

    def get_cropped_image_key(self):
        return Campaign.cropped_image_key(self.image_cropped_hash)

    def delete_cropped_image(self):
        # Verify that the hash isn't in use by other campaigns; can happen if they use the exact same image/selection
        if Campaign.objects.exclude(id=self.id).filter(image_cropped_hash=self.image_cropped_hash).exists():
            return

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(s3_bucket())
        bucket.delete_key(self.get_cropped_image_key())

    def generate_ga_event_label(self):
        return "%s/%s" % (self.id, self.title)

    @staticmethod
    def cropped_image_key(hash_):
        return "%s/%s.jpg" % (settings.AWS_CAMPAIGNS_PREFIX, hash_)

    @staticmethod
    def on(site):
        return Campaign.objects.filter(site=site)

    class Meta:
        ordering = ['-created']

@receiver(pre_delete, sender=Campaign, dispatch_uid="admin.models")
def delete_cropped_image(sender, **kwargs):
    # Delete cropped image from S3 on delete
    kwargs['instance'].delete_cropped_image()

class CampaignText(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='text')
    content = models.CharField(max_length=1024)
    style = models.CharField(max_length=1024) # JSON

    def render_style(self):
        style_string = ''
        for item, value in json.loads(self.style).items():
            style_string += '%s:%s;' % (item, value)
        return style_string

    class Meta:
        # The order isn't important but getting a *consistent* ordering can be helpful
        ordering = ['id']
