from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200)

class Search(models.Model):
    query = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)
