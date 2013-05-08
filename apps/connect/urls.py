from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('connect.views',
    url(r'^$', 'connect'),
)
