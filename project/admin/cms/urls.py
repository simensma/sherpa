from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.cms.views',

    # Pages
    url(r'^$', 'page.list'),
    url(r'^side/(?P<page>\d+)/$', 'page.edit'),
    url(r'^side/ny/$', 'page.new'),
    url(r'^side/slett/(?P<page>\d+)/$', 'page.delete'),

    # Menus
    url(r'^meny/ny/$', 'menu.new'),
    url(r'^meny/bytt/(?P<order1>\d+)/(?P<order2>\d+)/$', 'menu.swap'),
    url(r'^meny/slett/(?P<menu>\d+)/$', 'menu.delete'),

    # Versions
    url(r'^versjon/ny/(?P<variant>\d+)/$', 'version.new'),
    url(r'^editor/(?P<version>\d+)/$', 'version.edit'),

    # Rows
    url(r'^kolonner/ny/$', 'row.add_columns'),
    url(r'^rad/slett/(?P<row>\d+)/$', 'row.delete'),

    # Content
    url(r'^innhold/ny/$', 'content.add'),
    url(r'^innhold/slett/(?P<content>\d+)/$', 'content.delete'),
)
