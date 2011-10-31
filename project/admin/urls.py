from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.views',
    url(r'^$', 'index'),

    url(r'^side/$', 'page_list'),
    url(r'^side/ny/$', 'page_new'),
    url(r'^side/rediger/(?P<page>\d*)/$', 'page_edit'),
    url(r'^side/slett/(?P<page>\d*)/$', 'page_delete'),

    url(r'^meny/$', 'menu_list'),
    url(r'^meny/rediger/$', 'menu_edit'),
)
