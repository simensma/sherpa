from django.db import models

class Page(models.Model):
    content = models.TextField()
    slug = models.CharField(max_length="50")
