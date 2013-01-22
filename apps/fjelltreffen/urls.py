from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fjelltreffen.views',
    url(r'^$', 'index'),
    url(r'^last/(?P<start_index>\d+)/$', 'load'),
    url(r'^vis/(?P<id>\d+)/$', 'show'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<id>\d+)/$', 'edit'),
    url(r'^mine/$', 'mine'),
    url(r'^lagre/$', 'save'),
    url(r'^svar/$', 'reply'),
    url(r'^slett/(?P<id>\d+)/$', 'delete'),
)
