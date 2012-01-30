from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cms.views',

    # Pages
    url(r'^$', 'page.list'),
    url(r'^ny/$', 'page.new'),
    url(r'^rediger/(?P<page>\d+)/$', 'page.edit'),
    url(r'^slett/(?P<page>\d+)/$', 'page.delete'),

    # Variants
    url(r'^variant/ny/(?P<page>\d+)/$', 'variant.new'),
    url(r'^variant/rediger/(?P<version>\d+)/$', 'variant.edit'),
    url(r'^variant/bytt/(?P<page>\d+)/(?P<pri1>\d+)/(?P<pri2>\d+)/$', 'variant.swap'),
    #url(r'^variant/slett/(?P<variant>\d*)/$', 'delete'),

    # Versions
    url(r'^versjon/ny/(?P<variant>\d+)/$', 'version.new'),
    url(r'^versjon/rediger/(?P<version>\d+)/$', 'version.edit'),
    url(r'^versjon/aktiver/(?P<version>\d+)/$', 'version.activate'),

    # Layouts
    url(r'^versjon/layout/ny/(?P<version>\d+)/(?P<template>[a-zA-Z0-9-_]+)/$', 'layout.add'),
    url(r'^versjon/layout/flytt-ned/(?P<layout>\d+)/$', 'layout.move_down'),
    url(r'^versjon/layout/flytt-opp/(?P<layout>\d+)/$', 'layout.move_up'),
    url(r'^versjon/layout/slett/(?P<layout>\d+)/$', 'layout.delete'),

    # Widgets
    url(r'^widget/opprett/sitat/$', 'widgets.add_quote'),
    url(r'^widget/oppdater/sitat/$', 'widgets.edit_quote'),
    url(r'^widget/opprett/promo/$', 'widgets.add_promo'),
    url(r'^widget/oppdater/promo/$', 'widgets.edit_promo'),
    url(r'^widget/slett/(?P<widget>\d+)/$', 'widgets.delete'),

    # Content
    url(r'^innhold/opprett/$', 'content.create'),
    url(r'^innhold/oppdater/(?P<content>\d+)/$', 'content.update'),
    url(r'^innhold/slett/(?P<content>\d+)/$', 'content.delete'),

    # Menus
    url(r'^meny/$', 'menu.list'),
    url(r'^meny/ny/(?P<page>\d+)/$', 'menu.add'),
    url(r'^meny/bytt/(?P<pos1>\d+)/(?P<pos2>\d+)/$', 'menu.swap'),
    url(r'^meny/slett/(?P<page>\d+)/$', 'menu.remove'),
)
