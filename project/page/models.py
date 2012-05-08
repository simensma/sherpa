from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db import models
from django.db.models import Min

import json

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
    publisher = models.ForeignKey('user.Profile')

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
    active = models.BooleanField()
    title = None
    lede = None
    thumbnail = None
    hide_thumbnail = False

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
    type = models.CharField(max_length=1, choices=(('widget', 'Widget'), ('html', 'HTML'), ('image', 'Image'), ('title', 'Title')))
    # Note: 'order' should be unique, but it's not enforced because
    # when deleting and cascading orders, two orders will temporarily clash.
    order = models.IntegerField()

@receiver(pre_delete, sender=Content, dispatch_uid="page.models")
def delete_content(sender, **kwargs):
    for content in Content.objects.filter(column=kwargs['instance'].column, order__gt=kwargs['instance'].order):
        content.order = (content.order-1)
        content.save();
