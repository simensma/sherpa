# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('core.views',
    url(r'^postnummer/$', 'zipcode'),
    url(r'^tags/filter/$', 'filter_tags'),
    url(r'^kreditering/$', 'attribution'),
    url(r'^geosok/fylker/$', 'county_lookup'),
    url(r'^geosok/kommuner/$', 'municipality_lookup'),
    url(r'^doge/$', 'doge'),
    url(r'^booking/ledige-plasser/(?P<code>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/$', 'booking_spots'),
)
