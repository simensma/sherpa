from django.db import models

class Page(models.Model):
    slug = models.CharField(max_length=50)
    active = models.ForeignKey('page.PageContent')

class PageContent(models.Model):
    version = models.DecimalField(max_digits=4, decimal_places=1)
    content = models.TextField()
