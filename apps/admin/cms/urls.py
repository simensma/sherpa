# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cms.views',

    # Pages
    url(r'^$', 'page.list'),
    url(r'^side/barn/(?P<page>\d+)/$', 'page.children'),
    url(r'^side/ny/$', 'page.new'),
    url(r'^side/ny/unik/$', 'page.check_slug'),
    url(r'^side/slett/(?P<page>\d+)/$', 'page.delete'),
    url(r'^editor/(?P<version>\d+)/$', 'page.edit_version'),
    url(r'^editor/lagre/(?P<version>\d+)/$', 'content.save'),
    url(ur'^forhåndsvisning/(?P<version>\d+)/$', 'page.preview'),

    # Menus
    url(r'^meny/ny/$', 'menu.new'),
    url(r'^meny/rediger/(?P<menu>\d+)/$', 'menu.edit'),
    url(r'^meny/sorter/$', 'menu.reorder'),
    url(r'^meny/slett/(?P<menu>\d+)/$', 'menu.delete'),

    # Rows
    url(r'^kolonner/ny/$', 'row.add_columns'),
    url(r'^rad/slett/(?P<row>\d+)/$', 'row.delete'),

    # Content
    url(r'^widget/$', 'content.render_widget'),
)
