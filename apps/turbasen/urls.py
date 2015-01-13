# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('turbasen.views',
    url(r'^omrader/geosok/$', 'location_lookup'),
)
