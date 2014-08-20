from datetime import date
import random
import json
import re
import time

from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.cache import cache

import boto

from core.util import s3_bucket

class Menu(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=2048)
    # Even though this should be unique, it's not enforced because
    # when swapping, two orders will temporarily clash.
    order = models.IntegerField()
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return Menu.objects.filter(site=site)

@receiver(pre_delete, sender=Menu, dispatch_uid="page.models")
def delete_menu(sender, **kwargs):
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

    def __unicode__(self):
        return u'%s' % self.pk

    def get_rows(self):
        # Cache the results in a local attribute on this object
        if not hasattr(self, '_rows'):
            self._rows = Row.objects.filter(version=self).order_by('order')
        return self._rows

    def get_title_content(self):
        # Cache the results in a local attribute on this object
        if not hasattr(self, '_title'):
            self._title = Content.objects.get(column__row__version=self, type='title')
        return self._title

    def get_lede_content(self):
        # Cache the results in a local attribute on this object
        if not hasattr(self, '_lede'):
            self._lede = Content.objects.get(column__row__version=self, type='lede')
        return self._lede

    def get_thumbnail(self, size='small'):
        """Return a dict with two keys:
        - hide: True if this item shouldn't show a thumbnail
        - url: The URL to the thumbnail image (None if hide is True)
        The result of the method is cached.
        This logic is old and kind of weird, it might need review"""
        thumbnail = cache.get('version.%s.thumbnail.%s' % (self.id, size))
        if thumbnail is None:
            if self.variant.article.hide_thumbnail:
                thumbnail = {
                    'hide': True,
                    'url': None,
                }
            else:
                if self.variant.article.thumbnail is not None:
                    thumbnail = {
                        'hide': False,
                        'url': self.variant.article.thumbnail,
                    }
                else:
                    try:
                        # Define "main image" as the earliest one occurring (sorted by row, column, content)
                        content = Content.objects.filter(
                            column__row__version=self,
                            type='image'
                        ).order_by('column__row__order', 'column__order', 'order')[0]
                        thumbnail = {
                            'hide': False,
                            'url': json.loads(content.content)['src'],
                        }
                    except IndexError:
                        # There are no images in this article (shouldn't really happen)
                        thumbnail = {
                            'hide': True,
                            'url': None,
                        }

                # Statically use the 150px version. This should be optimized; save
                # the available sizes with the model and use the smallest appropriate one.
                if thumbnail['url'] is not None and s3_bucket() in thumbnail['url']:
                    if size == 'small':
                        size_string = str(min(settings.THUMB_SIZES))
                    else:
                        size_string = str(settings.THUMB_SIZES[-2])
                    t = thumbnail['url']
                    # Remove previous size spec if existing
                    t = re.sub('-\d+\.', '.', t)
                    thumbnail['url'] = '%s-%s%s' % (
                        t[:t.rfind('.')],
                        size_string,
                        t[t.rfind('.'):]
                    )

        cache.set('version.%s.thumbnail.%s' % (self.id, size), thumbnail, 60 * 60 * 24)
        return thumbnail

    def get_medium_thumbnail(self):
        return self.get_thumbnail(size='medium')

    def get_children_count(self):
        return Version.objects.filter(variant__page__parent=self.variant.page, active=True).count()

    def get_publishers(self):
        return sorted(self.publishers.all(), key=lambda u: u.get_full_name())

@receiver(post_delete, sender=Version, dispatch_uid="page.models")
def delete_page_version(sender, **kwargs):
    Row.objects.filter(version=kwargs['instance']).delete()

### CMS

class Row(models.Model):
    version = models.ForeignKey('page.Version', related_name='rows')
    order = models.IntegerField()

    def get_columns(self):
        # Cache the results in a local attribute on this object
        if not hasattr(self, '_columns'):
            self._columns = Column.objects.filter(row=self).order_by('order')
        return self._columns

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

    def get_contents(self):
        # Cache the results in a local attribute on this object
        if not hasattr(self, '_contents'):
            self._contents = Content.objects.filter(column=self).order_by('order')
        return self._contents

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

    def get_content(self):
        """Returned the parsed json-content. Will be called many times per instance during render, so cache it in
        a local attribute"""
        if not hasattr(self, '_parsed_content'):
            self._parsed_content = json.loads(self.content)
        return self._parsed_content

    def get_image_source(self):
        if self.type != 'image':
            raise Exception("You can only call this method on image contents, check your code logic")

        source = self.get_content()['src']

        local_image_path = '%s/%s' % (s3_bucket(), settings.AWS_IMAGEGALLERY_PREFIX)
        local_image_path_ssl = '%s/%s' % (s3_bucket(ssl=True), settings.AWS_IMAGEGALLERY_PREFIX)

        if not local_image_path in source and not local_image_path_ssl in source:
            # Not an image from the image gallery; don't touch it
            return source

        for size in settings.THUMB_SIZES:
            if ('-%s') % size in source:
                return source

        column_size = settings.COLUMN_SPAN_MAP[12 / self.column.span]
        if column_size > max(settings.THUMB_SIZES):
            # No thumbs are large enough, use the original
            # Not technically possible right now (the largest column is 940px and the largest thumb is 1880)
            return source
        else:
            thumb_size = min([t for t in settings.THUMB_SIZES if t >= column_size])

        name, extension = source.rsplit('.', 1)
        return '%s-%s.%s' % (name, thumb_size, extension)

    def get_cropping_json(self):
        if self.type != 'image':
            raise Exception("You can only call this method on image contents, check your code logic")

        content = self.get_content()
        if 'crop' in content:
            return json.dumps(content['crop'])
        else:
            return None

    def render_widget(self, request, current_site, admin_context=False):
        """Render this widget (obviously only applicable for widget-content) in the context of the given site"""
        from page.widgets.util import render_widget
        if self.type != 'widget':
            raise Exception("render_widget called on Content of type '%s'" % self.type)

        return render_widget(request, self.get_content(), current_site, admin_context=admin_context, content_id=self.id)

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
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    def url(self):
        return "//%s/%s%s.%s" % (s3_bucket(ssl=True), settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension)

    def has_fallback(self):
        return self.fallback_sha1_hash is not None and self.fallback_extension is not None

    def fallback_url(self):
        return "//%s/%s%s.%s" % (s3_bucket(ssl=True), settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension)

    def is_adform_script(self):
        return self.content_type == Ad.ADFORM_SCRIPT_CONTENT_TYPE

    def render_adform_script(self, placement):
        script = self.content_script

        # Change the URL to go via our counter
        pat = r'(\<a href=\")(.+?)(\")'
        rep = r'\1%s\3' % placement.destination_url()
        script = re.sub(pat, rep, script)

        # Set timestamp to current unix time
        script = re.sub(r'\[timestamp\]', str(int(time.time())), script)
        return script

    def delete_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(sha1_hash=self.sha1_hash).exists():
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(s3_bucket())
            bucket.delete_key("%s%s.%s" % (settings.AWS_ADS_PREFIX, self.sha1_hash, self.extension))

    def delete_fallback_file(self):
        # Check that other ads aren't using the same image file
        if not Ad.objects.exclude(id=self.id).filter(fallback_sha1_hash=self.fallback_sha1_hash).exists():
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(s3_bucket())
            bucket.delete_key("%s%s.%s" % (settings.AWS_ADS_PREFIX, self.fallback_sha1_hash, self.fallback_extension))

    @staticmethod
    def on(site):
        return Ad.objects.filter(site=site)

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
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    def destination_url(self):
        return self.ad.destination

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
    def on(site):
        return AdPlacement.objects.filter(site=site)

    @staticmethod
    def get_active_ad(site, count_view=True):
        ads = AdPlacement.on(site).filter(
            Q(start_date__lte=date.today(), end_date__gte=date.today(), view_limit__isnull=True) |
            Q(views__lt=F('view_limit'), start_date__isnull=True)
        )

        if len(ads) == 0:
            return None

        ad = ads[random.randint(0, len(ads) - 1)]

        if count_view:
            ad.views += 1
            ad.save()

        return ad
