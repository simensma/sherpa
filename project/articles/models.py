from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)
    publisher = models.ForeignKey('user.Profile')
