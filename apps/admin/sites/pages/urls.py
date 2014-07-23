# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.pages',

    # Pages
    url(r'^$', 'page.list'),
    url(r'^side/barn/$', 'page.children'),
    url(r'^side/ny/$', 'page.new'),
    url(r'^side/ny/unik/$', 'page.check_slug'),
    url(r'^side/slett/(?P<page>\d+)/$', 'page.delete'),
    url(r'^editor/(?P<version>\d+)/$', 'page.edit'),
    url(r'^editor/lagre/(?P<version>\d+)/$', 'content.save'),
    url(ur'^forhåndsvisning/(?P<version>\d+)/$', 'page.preview'),

    # Content
    url(r'^widget/$', 'content.reload_raw_widget'),
)
