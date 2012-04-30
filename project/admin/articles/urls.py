from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.articles.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'new'),
    url(r'^bilde/(?P<article>\d+)/$', 'image'),
    url(r'^bilde/(?P<article>\d+)/slett/$', 'image_delete'),
    url(r'^editor/(?P<version>\d+)/$', 'edit_version'),
    url(r'^publiser/(?P<article>\d+)/$', 'publish'),
    url(r'^slett/(?P<article>\d+)/$', 'delete'),
)
