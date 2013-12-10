from django.db.models.signals import pre_delete, post_delete
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db import models
from django.db.models import Q, F
from django.conf import settings

from datetime import date
import random
import json
import re
import simples3
import time

class Menu(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=2048)
    # Even though this should be unique, it's not enforced because
    # when swapping, two orders will temporarily clash.
    order = models.IntegerField()
    # Used to mark the current active menu page
    active = None
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return Menu.objects.filter(site=site)

@receiver(pre_delete, sender=Menu, dispatch_uid="page.models")
def delete_content(sender, **kwargs):
    for menu in Menu.on(kwargs['instance'].site).filter(order__gt=kwargs['instance'].order):
        menu.order = (menu.order-1)
        menu.save();

class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    created_by = models.ForeignKey('user.User', related_name='pages_created')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey('user.User', related_name='pages_modified', null=True)
    modified_date = models.DateTimeField(null=True)
    parent = models.ForeignKey('page.Page', null=True)
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return Page.objects.filter(site=site)

@receiver(post_delete, sender=Page, dispatch_uid="page.models")
def delete_page(sender, **kwargs):
    Variant.objects.filter(page=kwargs['instance']).delete()

class Variant(models.Model):
    # Exactly one of these foreign keys should be referenced (not null)
    page = models.ForeignKey('page.Page', null=True)
    article = models.ForeignKey('articles.Article', null=True)

    name = models.CharField(max_length=255)
    segment = models.ForeignKey('analytics.Segment', null=True)
    priority = models.IntegerField()
    # probability
    owner = models.ForeignKey('user.User', related_name='+')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

    def __unicode__(self):
        return u'%s' % self.pk

@receiver(post_delete, sender=Variant, dispatch_uid="page.models")
def delete_page_variant(sender, **kwargs):
    # Note: We don't really need to cascade priorities
    Version.objects.filter(variant=kwargs['instance']).delete()

class Version(models.Model):
    variant = models.ForeignKey('page.Variant')
    version = models.IntegerField()
    owner = models.ForeignKey('user.User', related_name='+')
    publishers = models.ManyToManyField('user.User', related_name='versions')
    active = models.BooleanField()
    tags = models.ManyToManyField('core.Tag', related_name='versions')
    ads = models.BooleanField()
    title = None
    lede = None
    thumbnail = None
    hide_thumbnail = False
    children = None # Used in page listing

    def __unicode__(self):
        return u'%s' % self.pk

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
                # Define "main image" as the first one in the first column and row
                content = Content.objects.filter(column__order=0, column__row__order=0,
                    column__row__version=self, type='image').order_by('order')[0]
                self.thumbnail = json.loads(content.content)['src']
            except IndexError:
                # There are no images in this article
                self.hide_thumbnail = True
        # Statically use the 150px version. This should be optimized; save
        # the available sizes with the model and use the smallest appropriate one.
        if self.thumbnail is not None and settings.AWS_BUCKET in self.thumbnail:
            t = self.thumbnail
            # Remove previous size spec if existing
            t = re.sub('-\d+\.', '.', t)
            self.thumbnail = t[:t.rfind('.')] + '-' + str(min(settings.THUMB_SIZES)) + t[t.rfind('.'):]

@receiver(post_delete, sender=Version, dispatch_uid="page.models")
def delete_page_version(sender, **kwargs):
    Row.objects.filter(version=kwargs['instance']).delete()

### CMS

class Row(models.Model):
    version = models.ForeignKey('page.Version')
    order = models.IntegerField()
    columns = None

    def __unicode__(self):
        return u'%s' % self.pk

@receiver(post_delete, sender=Row, dispatch_uid="page.models")
def delete_row(sender, **kwargs):
    Column.objects.filter(row=kwargs['instance']).delete()

class Column(models.Model):
    row = models.ForeignKey('page.Row')
    span = models.IntegerField()
    offset = models.IntegerField()
    order = models.IntegerField()
    contents = None

    def __unicode__(self):
        return u'%s' % self.pk

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

    def __unicode__(self):
        return u'%s' % self.pk

@receiver(pre_delete, sender=Content, dispatch_uid="page.models")
def delete_content(sender, **kwargs):
    for content in Content.objects.filter(column=kwargs['instance'].column, order__gt=kwargs['instance'].order):
        content.order = (content.order-1)
        content.save();

### Advertisements

class Ad(models.Model):
    """
    We now have 3 types of ads; images, flash and adform scripts. They are separated by content_type.
    An adform script will have the content type in ADFORM_SCRIPT_CONTENT_TYPE and content_script
    will contain its pasted script tags.
    Flash will be application/x-shockwave-flash, and all other content types are images. They're uploaded
    to S3, with sha1_hash as their key.
    """

    ADFORM_SCRIPT_CONTENT_TYPE = 'application/vnd.turistforeningen.adform'

    name = models.CharField(max_length=200)
    extension = models.CharField(max_length=4)
    destination = models.CharField(max_length=2048)
    sha1_hash = models.CharField(max_length=40)
    content_script = models.CharField(max_length=1023, default='') # Empty for image/flash. Used for adform scripts.
    content_type = models.CharField(max_length=200)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    viewcounter = models.CharField(max_length=2048)
    fallback_extension = models.CharField(max_length=4, null=True)
    fallback_sha1_hash = models.CharField(max_length=40, null=True)
    fallback_content_type = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return u'%s' % self.pk

    def url(self):
        return "//%s/%s%s.%s" % (settings.AWS_BUCKET_SSL, settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension)

    def has_fallback(self):
        return self.fallback_sha1_hash is not None and self.fallback_extension is not None

    def fallback_url(self):
        return "//%s/%s%s.%s" % (settings.AWS_BUCKET_SSL, settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension)

    def is_adform_script(self):
        return self.content_type == Ad.ADFORM_SCRIPT_CONTENT_TYPE

    def render_adform_script(self, placement):
        script = self.content_script

        # Change the URL to go via our counter
        url = reverse('page.views.ad', args=[placement.id])
        pat = r'(\<a href=\")(.+?)(\")'
        rep = r'\1%s\3' % url
        script = re.sub(pat, rep, script)

        # Set timestamp to current unix time
        script = re.sub(r'\[timestamp\]', str(int(time.time())), script)
        return script

    def delete_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(sha1_hash=self.sha1_hash).exists():
            s3 = simples3.S3Bucket(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY, 'https://%s' % settings.AWS_BUCKET)
            s3.delete("%s%s.%s" % (settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension))

    def delete_fallback_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(fallback_sha1_hash=self.fallback_sha1_hash).exists():
            s3 = simples3.S3Bucket(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
                settings.AWS_SECRET_ACCESS_KEY, 'https://%s' % settings.AWS_BUCKET)
            s3.delete("%s%s.%s" % (settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension))

# Upon ad delete, delete the corresponding object from S3
@receiver(post_delete, sender=Ad, dispatch_uid="page.models")
def delete_ad(sender, **kwargs):
    kwargs['instance'].delete_file()
    kwargs['instance'].delete_fallback_file()

class AdPlacement(models.Model):
    ad = models.ForeignKey('page.Ad')
    view_limit = models.IntegerField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s' % self.pk

    def is_old(self): return self.end_date < date.today()
    def is_current(self): return self.start_date <= date.today() and self.end_date >= date.today()
    def is_new(self): return self.start_date > date.today()

    def time_state(self):
        if self.is_old(): return 'old'
        elif self.is_current(): return 'current'
        elif self.is_new(): return 'new'

    def view_state(self):
        if self.views < self.view_limit: return 'active'
        else: return 'inactive'

    def render_adform_script(self):
        return self.ad.render_adform_script(self)

    @staticmethod
    def get_active_ad():
        ads = AdPlacement.objects.filter(
            Q(start_date__lte=date.today(), end_date__gte=date.today(), view_limit__isnull=True) |
            Q(views__lt=F('view_limit'), start_date__isnull=True))

        if len(ads) == 0:
            return None
        ad = ads[random.randint(0, len(ads) - 1)]
        ad.views += 1
        ad.save()
        return ad
