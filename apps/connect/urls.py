from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('connect.views',
    url(r'^bounce/$', 'connect', kwargs={'method': 'bounce'}),
    url(r'^signon/$', 'connect', kwargs={'method': 'signon'}),
    url(r'^signon/login/$', 'signon_login'),
)
