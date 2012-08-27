# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.articles.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'new'),
    url(r'^bilde/(?P<article>\d+)/$', 'image'),
    url(r'^bilde/(?P<article>\d+)/slett/$', 'image_delete'),
    url(r'^bilde/(?P<article>\d+)/skjul/$', 'image_hide'),
    url(r'^editor/(?P<version>\d+)/$', 'edit_version'),
    url(r'^forfattere/(?P<article>\d+)/$', 'update_publishers'),
    # Wanted to use 'ø' here, but ajax in IE8 didn't work with that ;_;
    url(r'^nokkelord/(?P<version>\d+)/$', 'update_tags'),
    url(ur'^forhåndsvisning/(?P<version>\d+)/$', 'preview'),
    url(r'^publiser/(?P<article>\d+)/$', 'publish'),
    url(r'^slett/(?P<article>\d+)/$', 'delete'),
    url(r'^slett/sikker/(?P<article>\d+)/$', 'confirm_delete'),
)
