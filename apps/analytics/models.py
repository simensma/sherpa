from django.db import models

class Search(models.Model):
    query = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return Search.objects.filter(site=site)

class NotFound(models.Model):
    path = models.CharField(max_length=2048)
    date = models.DateTimeField()
    site = models.ForeignKey('core.Site')

    def __unicode__(self):
        return u'%s' % self.pk

    @staticmethod
    def on(site):
        return NotFound.objects.filter(site=site)

class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __unicode__(self):
        return u'%s' % self.pk

    def match(self, request):
        if   self.name == 'opera': return self.matchOpera(request)
        elif self.name == 'firefox': return self.matchFirefox(request)
        else: return False # TODO: Log an error here, we're not supposed to receive an undefined segment

    def matchOpera(self, request):
        return (request.META['HTTP_USER_AGENT'].find("Opera") != -1)

    def matchFirefox(self, request):
        return (request.META['HTTP_USER_AGENT'].find("Firefox") != -1)
