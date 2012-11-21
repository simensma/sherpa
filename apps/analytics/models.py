from django.db import models

class Segment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def match(self, request):
        if   self.name == 'opera': return self.matchOpera(request)
        elif self.name == 'firefox': return self.matchFirefox(request)
        else: return False # TODO: Log an error here, we're not supposed to receive an undefined segment

    def matchOpera(self, request):
        return (request.META['HTTP_USER_AGENT'].find("Opera") != -1)

    def matchFirefox(self, request):
        return (request.META['HTTP_USER_AGENT'].find("Firefox") != -1)
