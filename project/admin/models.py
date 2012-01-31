from django.db import models

class Image(models.Model):
    hash = models.CharField(max_length=40)
    album = models.ForeignKey('admin.Album')
    photographer = models.CharField(max_length=200)
    credits = models.CharField(max_length=20)
    photographer_contact = models.CharField(max_length=200)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('users.Profile')
    height = models.IntegerField()
    width = models.IntegerField()

class Album(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('admin.Album', null=True)
    # Todo: Author, or some other sort of affiliation?

class Keyword(models.Model):
    image = models.ForeignKey('admin.Image')
    name = models.CharField(max_length=200)
