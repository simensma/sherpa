from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

from page.models import Variant

class Article(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    publisher = models.ForeignKey('user.Profile')

@receiver(post_delete, sender=Article, dispatch_uid="articles.models")
def delete_article(sender, **kwargs):
    Variant.objects.filter(article=kwargs['instance']).delete()
