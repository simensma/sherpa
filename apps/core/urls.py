# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^postnummer/$', 'zipcode'),
    url(r'^tags/filter/$', 'filter_tags'),
    url(r'^kreditering/$', 'attribution'),
    url(r'^geosok/fylker/$', 'county_lookup'),
    url(r'^geosok/kommuner/$', 'municipality_lookup'),
    url(r'^doge/$', 'doge'),
)
