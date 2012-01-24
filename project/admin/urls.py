from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.views',
    url(r'^$', 'index'),

    # Pages
    url(r'^artikkel/$', 'page_list'),
    url(r'^artikkel/ny/$', 'page_new'),
    url(r'^artikkel/rediger/(?P<page>\d+)/$', 'page_edit'),
    url(r'^artikkel/slett/(?P<page>\d+)/$', 'page_delete'),

    # Variants
    url(r'^artikkel/variant/ny/(?P<page>\d+)/$', 'variant_new'),
    url(r'^artikkel/variant/rediger/(?P<version>\d+)/$', 'variant_edit'),
    url(r'^artikkel/variant/bytt/(?P<page>\d+)/(?P<pri1>\d+)/(?P<pri2>\d+)/$', 'variant_swap'),
    #url(r'^artikkel/variant/slett/(?P<variant>\d*)/$', 'variant_delete'),

    # Versions
    url(r'^artikkel/versjon/ny/(?P<variant>\d+)/$', 'version_new'),
    url(r'^artikkel/versjon/rediger/(?P<version>\d+)/$', 'version_edit'),
    url(r'^artikkel/versjon/aktiver/(?P<version>\d+)/$', 'version_activate'),
    url(r'^artikkel/versjon/layout/ny/(?P<version>\d+)/(?P<template>[a-zA-Z0-9-_]+)/$', 'layout_add'),
    url(r'^artikkel/versjon/layout/flytt-ned/(?P<layout>\d+)/$', 'layout_move_down'),
    url(r'^artikkel/versjon/layout/flytt-opp/(?P<layout>\d+)/$', 'layout_move_up'),
    url(r'^artikkel/versjon/layout/slett/(?P<layout>\d+)/$', 'layout_delete'),

    # Widgets
    url(r'^artikkel/widget/opprett/quote/(?P<version>\d+)/$', 'version_add_widget_quote'),
    url(r'^artikkel/widget/slett/(?P<widget>\d+)/$', 'widget_delete'),

    # Content
    url(r'^artikkel/innhold/opprett/(?P<layout>\d+)/(?P<column>\d+)/(?P<order>\d+)/$', 'content_create'),
    url(r'^artikkel/innhold/oppdater/(?P<content>\d+)/$', 'content_update'),
    url(r'^artikkel/innhold/slett/(?P<content>\d+)/$', 'content_delete'),

    # Menus
    url(r'^meny/$', 'menu_list'),
    url(r'^meny/ny/(?P<page>\d+)/$', 'menu_add'),
    url(r'^meny/bytt/(?P<pos1>\d+)/(?P<pos2>\d+)/$', 'menu_swap'),
    url(r'^meny/slett/(?P<page>\d+)/$', 'menu_remove'),

    # Analytics
    url(r'^analyse/$', 'analytics_visitors_list'),
    url(r'^analyse/sidevisninger/(?P<visitor>\d+)/$', 'analytics_requests_list'),
)
