# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.articles.views',
    url(r'^$', 'list'),
    url(r'^last/$', 'list_load'),
    url(r'^ny/$', 'new'),
    url(r'^bilde/(?P<article>\d+)/$', 'image'),
    url(r'^bilde/(?P<article>\d+)/slett/$', 'image_delete'),
    url(r'^bilde/(?P<article>\d+)/skjul/$', 'image_hide'),
    url(r'^editor/(?P<version>\d+)/$', 'edit_version'),
    url(ur'^forhåndsvisning/(?P<version>\d+)/$', 'preview'),
    url(r'^slett/(?P<article>\d+)/$', 'delete'),
    url(r'^slett/sikker/(?P<article>\d+)/$', 'confirm_delete'),
)
