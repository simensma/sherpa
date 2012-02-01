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

    # Blocks
    url(r'^blokk/ny/(?P<version>\d+)/(?P<template>[a-zA-Z0-9-_]+)/$', 'block.add'),
    url(r'^blokk/flytt-ned/(?P<block>\d+)/$', 'block.move_down'),
    url(r'^blokk/flytt-opp/(?P<block>\d+)/$', 'block.move_up'),
    url(r'^blokk/slett/(?P<block>\d+)/$', 'block.delete'),

    # Widgets
    url(r'^widget/opprett/sitat/$', 'widget.add_quote'),
    url(r'^widget/oppdater/sitat/$', 'widget.edit_quote'),
    url(r'^widget/opprett/promo/$', 'widget.add_promo'),
    url(r'^widget/oppdater/promo/$', 'widget.edit_promo'),
    url(r'^widget/slett/(?P<widget>\d+)/$', 'widget.delete'),

    # Content
    url(r'^innhold/opprett/$', 'content.create'),
    url(r'^innhold/oppdater/(?P<content>\d+)/$', 'content.update'),
    url(r'^innhold/slett/(?P<content>\d+)/$', 'content.delete'),

    # Menus
    url(r'^meny/$', 'menu.list'),
    url(r'^meny/ny/$', 'menu.new'),
    url(r'^meny/bytt/(?P<order1>\d+)/(?P<order2>\d+)/$', 'menu.swap'),
    url(r'^meny/slett/(?P<menu>\d+)/$', 'menu.delete'),
)
