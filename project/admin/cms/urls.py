from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cms.views',

    # Pages
    url(r'^$', 'page.page_list'),
    url(r'^ny/$', 'page.page_new'),
    url(r'^rediger/(?P<page>\d+)/$', 'page.page_edit'),
    url(r'^slett/(?P<page>\d+)/$', 'page.page_delete'),

    # Variants
    url(r'^variant/ny/(?P<page>\d+)/$', 'variant.variant_new'),
    url(r'^variant/rediger/(?P<version>\d+)/$', 'variant.variant_edit'),
    url(r'^variant/bytt/(?P<page>\d+)/(?P<pri1>\d+)/(?P<pri2>\d+)/$', 'variant.variant_swap'),
    #url(r'^variant/slett/(?P<variant>\d*)/$', 'variant_delete'),

    # Versions
    url(r'^versjon/ny/(?P<variant>\d+)/$', 'variant.version_new'),
    url(r'^versjon/rediger/(?P<version>\d+)/$', 'variant.version_edit'),
    url(r'^versjon/aktiver/(?P<version>\d+)/$', 'variant.version_activate'),
    url(r'^versjon/layout/ny/(?P<version>\d+)/(?P<template>[a-zA-Z0-9-_]+)/$', 'variant.layout_add'),
    url(r'^versjon/layout/flytt-ned/(?P<layout>\d+)/$', 'variant.layout_move_down'),
    url(r'^versjon/layout/flytt-opp/(?P<layout>\d+)/$', 'variant.layout_move_up'),
    url(r'^versjon/layout/slett/(?P<layout>\d+)/$', 'variant.layout_delete'),

    # Widgets
    url(r'^widget/opprett/sitat/$', 'widgets.add_widget_quote'),
    url(r'^widget/oppdater/sitat/$', 'widgets.edit_widget_quote'),
    url(r'^widget/opprett/promo/$', 'widgets.add_widget_promo'),
    url(r'^widget/oppdater/promo/$', 'widgets.edit_widget_promo'),
    url(r'^widget/slett/(?P<widget>\d+)/$', 'widgets.widget_delete'),

    # Content
    url(r'^innhold/opprett/$', 'variant.content_create'),
    url(r'^innhold/oppdater/(?P<content>\d+)/$', 'variant.content_update'),
    url(r'^innhold/slett/(?P<content>\d+)/$', 'variant.content_delete'),

    # Menus
    url(r'^meny/$', 'menu.menu_list'),
    url(r'^meny/ny/(?P<page>\d+)/$', 'menu.menu_add'),
    url(r'^meny/bytt/(?P<pos1>\d+)/(?P<pos2>\d+)/$', 'menu.menu_swap'),
    url(r'^meny/slett/(?P<page>\d+)/$', 'menu.menu_remove'),
)
