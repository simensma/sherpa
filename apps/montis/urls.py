# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('montis.views',
    url(r'^booking/ledige-plasser/(?P<code>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/$', 'booking_spots'),
)
