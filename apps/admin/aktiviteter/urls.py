# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/beskrivelse/(?P<aktivitet>\d+)/$', 'edit_description'),
    url(r'^rediger/dato-forhandsvisning/$', 'edit_description_date_preview'),
    url(r'^rediger/pameldte/(?P<aktivitet>\d+)/$', 'edit_participants'),
    url(ur'^turledersøk/$', 'turleder_search'),
)
