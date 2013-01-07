from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fjelltreffen.views',
    url(r'^$', 'index'),
    #url(r'^(?P<id>\d+)/$', 'page'),
    url(r'^vis/(?P<id>\d+)/$', 'show'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<id>\d+)/$', 'edit'),
    url(r'^mine/$', 'mine'),
    url(r'^save/$', 'save'),
    url(r'^delete/(?P<id>\d+)/$', 'delete'),
)