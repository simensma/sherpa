from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fjelltreffen.views',
    url(r'^$', 'index'),
    url(r'^last/(?P<start_index>\d+)/$', 'load'),
    url(r'^vis/(?P<id>\d+)/$', 'show'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<id>\d+)/$', 'edit'),
    url(r'^mine/$', 'mine'),
    url(r'^lagre/$', 'save'),
    url(r'^svar/(?P<id>\d+)/$', 'reply'),
    url(r'^svart/(?P<id>\d+)/$', 'show_reply_sent'),
    url(r'^slett/(?P<id>\d+)/$', 'delete'),
    url(r'^mine/vis/(?P<id>\d+)/$', 'show_mine'),
    url(r'^mine/skjul/(?P<id>\d+)/$', 'hide_mine'),
    url(r'^aldersgrense/$', 'too_young'),
)
