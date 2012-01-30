from django.db import models

class Image(models.Model):
    hash = models.CharField(max_length=40)
    # Todo: Loads of metadata
    album = models.ForeignKey('admin.Album')
    #page = models.ForeignKey('page.Page', unique=True)
    position = models.IntegerField(unique=True)

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)
    # Todo: Author, or some other sort of affiliation?
