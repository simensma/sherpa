# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('admin.sites.articles.views',
    url(r'^$', 'list'),
    url(r'^last/$', 'list_load'),
    url(r'^ny/$', 'new'),
    url(r'^editor/(?P<version>\d+)/$', 'edit'),
    url(ur'^forhåndsvisning/(?P<version>\d+)/$', 'preview'),
    url(r'^slett/(?P<article>\d+)/$', 'delete'),
    url(r'^slett/sikker/(?P<article>\d+)/$', 'confirm_delete'),
)
