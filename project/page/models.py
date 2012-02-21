from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page', unique=True)
    # Even though this should be unique, it's not enforced because
    # when swapping, two orders will temporarily clash.
    order = models.IntegerField()

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=50, unique=True)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    publisher = models.ForeignKey('user.Profile')

@receiver(post_delete, sender=Page)
def delete_page(sender, **kwargs):
    Menu.objects.filter(page=kwargs['instance']).delete()
    PageVariant.objects.filter(page=kwargs['instance']).delete()

class PageVariant(models.Model):
    # Exactly one of these foreign keys should be referenced (not null)
    page = models.ForeignKey('page.Page', null=True)
    article = models.ForeignKey('articles.Article', null=True)

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment', null=True)
    priority = models.IntegerField()
    # probability
    publisher = models.ForeignKey('user.Profile')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

@receiver(post_delete, sender=PageVariant)
def delete_page_variant(sender, **kwargs):
    # Note: We don't really need to cascade priorities
    PageVersion.objects.filter(variant=kwargs['instance']).delete()

class PageVersion(models.Model):
    variant = models.ForeignKey('page.PageVariant')
    version = models.IntegerField()
    publisher = models.ForeignKey('user.Profile')
    active = models.BooleanField()

@receiver(post_delete, sender=PageVersion)
def delete_page_version(sender, **kwargs):
    Row.objects.filter(version=kwargs['instance']).delete()

### CMS

class Row(models.Model):
    version = models.ForeignKey('page.PageVersion')
    order = models.IntegerField()
    columns = None

@receiver(post_delete, sender=Row)
def delete_row(sender, **kwargs):
    Column.objects.filter(row=kwargs['instance']).delete()

class Column(models.Model):
    row = models.ForeignKey('page.Row')
    span = models.IntegerField()
    order = models.IntegerField()
    contents = None

@receiver(post_delete, sender=Column)
def delete_column(sender, **kwargs):
    Content.objects.filter(column=kwargs['instance']).delete()

class Content(models.Model):
    column = models.ForeignKey('page.Column')
    content = models.TextField()
    type = models.CharField(max_length=1, choices=(('w', 'Widget'), ('h', 'HTML')))
    order = models.IntegerField()
    widget = None

@receiver(post_delete, sender=Content)
def delete_content(sender, **kwargs):
    for content in Content.objects.filter(column=self.column, order__get=order):
        content.order = (content.order-1)
        content.save();
