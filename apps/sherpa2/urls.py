# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('sherpa2.views',
    url(r'^geosok/omrader/$', 'location_lookup'),
)
