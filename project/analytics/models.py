from django.db import models

class Visitor(models.Model):
    profile = models.ForeignKey('auth.Profile', unique=True, null=True)

class Request(models.Model):
    visitor = models.ForeignKey('analytics.Visitor')
    url = models.CharField(max_length=2048)
    server_host = models.CharField(max_length=2048)
    client_ip = models.CharField(max_length=39) # Max char-length of ipv6
    client_host = models.CharField(max_length=2048, null=True)
    referrer = models.CharField(max_length=2048, null=True)
    enter = models.DateField()
    exit = models.DateField(default=None, null=True)
    # Hack?
    pageview = None

class Pageview(models.Model):
    request = models.ForeignKey('analytics.Request')
    variant = models.ForeignKey('page.PageVariant')
    activeVersion = models.ForeignKey('page.PageVersion')
    requestedSegment = models.ForeignKey('analytics.Segment', related_name='requested', null=True)
    matchedSegment = models.ForeignKey('analytics.Segment', related_name='matched', null=True)

class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def match(self, request, visitor):
        if   self.name == 'opera': return self.matchOpera(request, visitor)
        elif self.name == 'firefox': return self.matchFirefox(request, visitor)
        else: return False # Log an error here, we're not supposed to receive an undefined segment

    def matchOpera(self, request, visitor):
        return (request.META['HTTP_USER_AGENT'].find("Opera") != -1)

    def matchFirefox(self, request, visitor):
        return (request.META['HTTP_USER_AGENT'].find("Firefox") != -1)
