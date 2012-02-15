from django.db import models

class Image(models.Model):
    key = models.CharField(max_length=8)
    hash = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    album = models.ForeignKey('admin.Album')
    credits = models.CharField(max_length=20)
    photographer = models.CharField(max_length=200)
    photographer_contact = models.CharField(max_length=200)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('users.Profile')
    width = models.IntegerField()
    height = models.IntegerField()

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)
    # Todo: Author, or some other sort of affiliation?

class Keyword(models.Model):
    image = models.ForeignKey('admin.Image')
    name = models.CharField(max_length=200)
