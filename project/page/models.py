from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db import models
from django.db.models import Min
from django.conf import settings
from lib import S3

from admin.images.views import THUMB_SIZES
from datetime import date
import random
import json
import re

class Menu(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=2048)
    # Even though this should be unique, it's not enforced because
    # when swapping, two orders will temporarily clash.
    order = models.IntegerField()
    # Used to mark the current active menu page
    active = None

@receiver(pre_delete, sender=Menu, dispatch_uid="page.models")
def delete_content(sender, **kwargs):
    for menu in Menu.objects.filter(order__gt=kwargs['instance'].order):
        menu.order = (menu.order-1)
        menu.save();

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=50, unique=True)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    publisher = models.ForeignKey('user.Profile')
    parent = models.ForeignKey('page.Page', null=True)

@receiver(post_delete, sender=Page, dispatch_uid="page.models")
def delete_page(sender, **kwargs):
    Variant.objects.filter(page=kwargs['instance']).delete()

class Variant(models.Model):
    # Exactly one of these foreign keys should be referenced (not null)
    page = models.ForeignKey('page.Page', null=True)
    article = models.ForeignKey('articles.Article', null=True)

    name = models.CharField(max_length=200)
    segment = models.ForeignKey('analytics.Segment', null=True)
    priority = models.IntegerField()
    # probability
    publisher = models.ForeignKey('user.Profile')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

@receiver(post_delete, sender=Variant, dispatch_uid="page.models")
def delete_page_variant(sender, **kwargs):
    # Note: We don't really need to cascade priorities
    Version.objects.filter(variant=kwargs['instance']).delete()

class Version(models.Model):
    variant = models.ForeignKey('page.Variant')
    version = models.IntegerField()
    publisher = models.ForeignKey('user.Profile')
    publishers = models.ManyToManyField('user.Profile', related_name='versions')
    active = models.BooleanField()
    tags = models.ManyToManyField('admin.Tag', related_name='versions')
    title = None
    lede = None
    thumbnail = None
    hide_thumbnail = False
    children = None # Used in page listing

    def load_preview(self):
        self.title = Content.objects.get(column__row__version=self, type='title')
        self.lede = Content.objects.get(column__row__version=self, type='lede')
        if self.variant.article.hide_thumbnail:
            self.hide_thumbnail = True
            return
        if self.variant.article.thumbnail is not None:
            self.thumbnail = self.variant.article.thumbnail
        else:
            try:
                # Define "main image" as the one in the first column and row
                content = Content.objects.filter(column__order=0, column__row__order=0,
                    column__row__version=self, type='image')[0]
                self.thumbnail = json.loads(content.content)['src']
            except IndexError:
                # There are no images in this article
                self.hide_thumbnail = True
        # Statically use the 150px version. This should be optimized; save
        # the available sizes with the model and use the smallest appropriate one.
        if self.thumbnail != None and settings.AWS_BUCKET in self.thumbnail:
            t = self.thumbnail
            # Remove previous size spec if existing
            t = re.sub('-\d+\.', '.', t)
            self.thumbnail = t[:t.rfind('.')] + '-' + str(min(THUMB_SIZES)) + t[t.rfind('.'):]

@receiver(post_delete, sender=Version, dispatch_uid="page.models")
def delete_page_version(sender, **kwargs):
    Row.objects.filter(version=kwargs['instance']).delete()

### CMS

class Row(models.Model):
    version = models.ForeignKey('page.Version')
    order = models.IntegerField()
    columns = None

@receiver(post_delete, sender=Row, dispatch_uid="page.models")
def delete_row(sender, **kwargs):
    Column.objects.filter(row=kwargs['instance']).delete()

class Column(models.Model):
    row = models.ForeignKey('page.Row')
    span = models.IntegerField()
    offset = models.IntegerField()
    order = models.IntegerField()
    contents = None

@receiver(post_delete, sender=Column, dispatch_uid="page.models")
def delete_column(sender, **kwargs):
    Content.objects.filter(column=kwargs['instance']).delete()

class Content(models.Model):
    column = models.ForeignKey('page.Column')
    content = models.TextField()
    type = models.CharField(max_length=255, choices=(('widget', 'Widget'), ('html', 'HTML'), ('image', 'Image'), ('title', 'Title')))
    # Note: 'order' should be unique, but it's not enforced because
    # when deleting and cascading orders, two orders will temporarily clash.
    order = models.IntegerField()

@receiver(pre_delete, sender=Content, dispatch_uid="page.models")
def delete_content(sender, **kwargs):
    for content in Content.objects.filter(column=kwargs['instance'].column, order__gt=kwargs['instance'].order):
        content.order = (content.order-1)
        content.save();

### Advertisements

class Ad(models.Model):
    name = models.CharField(max_length=200)
    extension = models.CharField(max_length=4)
    destination = models.CharField(max_length=2048)
    sha1_hash = models.CharField(max_length=40)
    content_type = models.CharField(max_length=200)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    fallback_extension = models.CharField(max_length=4, null=True)
    fallback_sha1_hash = models.CharField(max_length=40, null=True)
    fallback_content_type = models.CharField(max_length=200, null=True)

    def url(self):
        return "//%s/%s%s.%s" % (settings.AWS_BUCKET_SSL, settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension)

    def fallback_url(self):
        return "//%s/%s%s.%s" % (settings.AWS_BUCKET_SSL, settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension)

    def delete_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(sha1_hash=self.sha1_hash).exists():
            conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            conn.delete(settings.AWS_BUCKET, "%s%s.%s" % (settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension))

    def delete_fallback_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(fallback_sha1_hash=self.fallback_sha1_hash).exists():
            conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            conn.delete(settings.AWS_BUCKET, "%s%s.%s" % (settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension))

# Upon ad delete, delete the corresponding object from S3
@receiver(post_delete, sender=Ad, dispatch_uid="page.models")
def delete_ad(sender, **kwargs):
    kwargs['instance'].delete_file()
    kwargs['instance'].delete_fallback_file()

class AdPlacement(models.Model):
    PLACEMENTS = (('core_frontpage', 'Forsiden'),
        ('articles', 'Artikler'),
        ('core_joint_trip', 'Fellesturer'),
        ('core_cabins', 'Hytter og ruter'),
        ('core_children', 'Barn'),
        ('core_youth', 'Ungdom'),
        ('core_mountainsports', 'Fjellsport'),
        ('core_senior', 'Senior'),
        ('core_school', 'Skole'),
        ('core_education', 'Kurs og utdanning'),
        ('core_accessibility', 'Tur for alle'),
        ('core_utno', 'UT.no'))

    ad = models.ForeignKey('page.Ad')
    start_date = models.DateField()
    end_date = models.DateField()
    placement = models.CharField(max_length=100, choices=PLACEMENTS)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    def is_old(self): return self.end_date < date.today()
    def is_current(self): return self.start_date <= date.today() and self.end_date >= date.today()
    def is_new(self): return self.start_date > date.today()

    def state(self):
        if self.is_old(): return 'old'
        elif self.is_current(): return 'current'
        elif self.is_new(): return 'new'

    @staticmethod
    def get_active_ad(page):
        ads = AdPlacement.objects.filter(start_date__lte=date.today(),
            end_date__gte=date.today(), placement=page)

        if len(ads) == 0:
            return None
        ad = ads[random.randint(0, len(ads) - 1)]
        ad.views += 1
        ad.save()
        return ad
