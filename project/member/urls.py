from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('member.views',
    url(r'^$', 'index'),
    url(r'^registrer', 'register'),
)
