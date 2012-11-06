from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

from page.models import Variant

class Article(models.Model):
    thumbnail = models.CharField(max_length=100, null=True)
    hide_thumbnail = models.BooleanField()
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    site = models.ForeignKey('core.Site')
    @staticmethod
    def on(site):
        return Menu.objects.filter(site=site)

@receiver(post_delete, sender=Article, dispatch_uid="articles.models")
def delete_article(sender, **kwargs):
    Variant.objects.filter(article=kwargs['instance']).delete()

class OldArticle(models.Model):
    title = models.CharField(max_length=255)
    lede = models.TextField()
    content = models.TextField()
    author_name = models.CharField(max_length=255)
    author_email = models.CharField(max_length=255)
    date = models.DateTimeField()
