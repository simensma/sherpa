# encoding: utf-8
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

from page.models import Variant

class Article(models.Model):
    thumbnail = models.CharField(max_length=2048, null=True)
    hide_thumbnail = models.BooleanField()
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    created_by = models.ForeignKey('user.User', related_name='articles_created')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey('user.User', related_name='articles_modified', null=True)
    modified_date = models.DateTimeField(null=True)
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return Article.objects.filter(site=site)

@receiver(post_delete, sender=Article, dispatch_uid="articles.models")
def delete_article(sender, **kwargs):
    Variant.objects.filter(article=kwargs['instance']).delete()

class OldArticle(models.Model):
    """
    These are old articles imported from Sherpa 2.
    We filtered on folder 15 (the old main page), but NOT on owner 56 (Den Norske Turistforening) or anything else.
    Note that old articles had a date_out field which was ignored.
    Se the 0008_import_old_articles migration for more details.
    """
    title = models.CharField(max_length=255)
    lede = models.TextField()
    content = models.TextField()
    author_name = models.CharField(max_length=255)
    author_email = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __unicode__(self):
        return u'%s' % self.pk
