# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<aktivitet>\d+)/$', 'edit'),
    url(r'^rediger/dato-forhandsvisning/$', 'edit_date_preview'),
    url(r'^pameldte/(?P<aktivitet>\d+)/$', 'participants'),
    url(ur'^turledersøk/$', 'turleder_search'),
)
