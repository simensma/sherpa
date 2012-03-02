from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cms.views',

    # Pages
    url(r'^$', 'page.list'),
    url(r'^side/(?P<page>\d+)/$', 'page.edit'),
    url(r'^side/ny/$', 'page.new'),
    url(r'^side/slett/(?P<page>\d+)/$', 'page.delete'),

    # Menus
    url(r'^meny/$', 'menu.list'),
    url(r'^meny/ny/$', 'menu.new'),
    url(r'^meny/bytt/(?P<order1>\d+)/(?P<order2>\d+)/$', 'menu.swap'),
    url(r'^meny/slett/(?P<menu>\d+)/$', 'menu.delete'),

    # Advanced editor
    url(r'^editor/avansert/(?P<version>\d+)/$', 'editor_advanced.edit'),

    # Variants
    url(r'^variant/ny/(?P<page>\d+)/$', 'variant.new'),
    url(r'^variant/bytt/(?P<page>\d+)/(?P<pri1>\d+)/(?P<pri2>\d+)/$', 'variant.swap'),
    url(r'^variant/slett/(?P<variant>\d*)/$', 'variant.delete'),

    # Versions
    url(r'^versjon/ny/(?P<variant>\d+)/$', 'version.new'),
    url(r'^versjon/aktiver/(?P<version>\d+)/$', 'version.activate'),

    # Rows
    url(r'^kolonner/ny/$', 'row.add_columns'),
    url(r'^rad/flytt-ned/(?P<block>\d+)/$', 'row.move_down'),
    url(r'^rad/flytt-opp/(?P<block>\d+)/$', 'row.move_up'),
    url(r'^rad/slett/(?P<block>\d+)/$', 'row.delete'),

    # Widgets
    url(r'^widget/opprett/sitat/$', 'widget.add_quote'),
    url(r'^widget/oppdater/sitat/$', 'widget.edit_quote'),
    url(r'^widget/opprett/promo/$', 'widget.add_promo'),
    url(r'^widget/oppdater/promo/$', 'widget.edit_promo'),
    url(r'^widget/slett/(?P<widget>\d+)/$', 'widget.delete'),

    # Content
    url(r'^innhold/ny/$', 'content.add'),
    url(r'^innhold/oppdater/(?P<content>\d+)/$', 'content.update'),
    url(r'^innhold/slett/(?P<content>\d+)/$', 'content.delete'),
)
