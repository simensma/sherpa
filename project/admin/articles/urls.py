from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.articles.views',
    url(r'^$', 'list'),
    url(r'^ny/$', 'new'),
    url(r'^oppdater/(?P<version>\d+)/$', 'save'),
    url(r'^slett/(?P<article>\d+)/$', 'delete'),
    url(r'^editor/(?P<version>\d+)/$', 'edit_version'),
)
