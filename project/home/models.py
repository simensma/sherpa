from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    version = models.ForeignKey('page.PageVersion')
    position = models.IntegerField()
