from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('connect.views',
    url(r'^bounce/$', 'bounce'),
    url(r'^signon/$', 'signon'),
    url(r'^signon/login/$', 'signon_login'),
)
