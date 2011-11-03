from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.views',
    url(r'^$', 'index'),

    # Sider
    url(r'^artikkel/$', 'page_list'),
    url(r'^artikkel/ny/$', 'page_new'),
    url(r'^artikkel/rediger/(?P<page>\d*)/$', 'page_edit'),
    url(r'^artikkel/slett/(?P<page>\d*)/$', 'page_delete'),

    # Versjoner
    url(r'^artikkel/versjon/ny/(?P<page>\d*)/$', 'page_version_new'),
    url(r'^artikkel/versjon/aktiver/(?P<version>\d*)/$', 'page_version_activate'),
    url(r'^artikkel/versjon/rediger/(?P<version>\d*)/$', 'page_version_edit'),

    # Varianter
    url(r'^artikkel/variant/ny/(?P<version>\d*)/$', 'page_variant_new'),
    url(r'^side/variant/bytt/(?P<version>\d*)/(?P<pri1>\d*)/(?P<pri2>\d*)/$', 'page_variant_swap'),
    url(r'^artikkel/variant/slett/(?P<variant>\d*)/$', 'page_variant_delete'),


    # Menyer
    url(r'^meny/$', 'menu_list'),
    url(r'^meny/ny/(?P<page>\d*)/$', 'menu_add'),
    url(r'^meny/bytt/(?P<pos1>\d*)/(?P<pos2>\d*)/$', 'menu_swap'),
    url(r'^meny/slett/(?P<page>\d*)/$', 'menu_remove'),
)
