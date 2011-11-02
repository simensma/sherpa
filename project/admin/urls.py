from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.views',
    url(r'^$', 'index'),

    # Sider
    url(r'^artikkel/$', 'page_list'),
    url(r'^artikkel/ny/$', 'page_new'),
    url(r'^artikkel/rediger/(?P<page>\d*)/(?P<version>\d*)/$', 'page_edit'),
    url(r'^artikkel/slett/(?P<page>\d*)/$', 'page_delete'),

    # Versjoner
    url(r'^artikkel/versjon/(?P<page>\d*)/$', 'page_version'),
    url(r'^artikkel/versjon/ny/(?P<page>\d*)/$', 'page_version_new'),
    url(r'^artikkel/versjon/aktiver/(?P<page>\d*)/(?P<version>\d*)/$', 'page_version_activate'),

    # Varianter
    url(r'^artikkel/variant/(?P<page>\d*)/(?P<version>\d*)/$', 'variant_list'),
#    url(r'^side/variant/ny/$', 'variant_new'),
#    url(r'^side/variant/rediger/(?P<page>\d*)/$', 'variant_edit'),
#    url(r'^side/variant/slett/(?P<page>\d*)/$', 'variant_delete'),


    # Menyer
    url(r'^meny/$', 'menu_list'),
    url(r'^meny/rediger/$', 'menu_edit'),
)
