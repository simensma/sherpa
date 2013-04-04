# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<aktivitet>\d+)/$', 'edit'),
    url(r'^ny/dato/$', 'new_aktivitet_date'),
    url(r'^rediger/dato/(?P<aktivitet_date>\d+)/$', 'edit_aktivitet_date'),
    url(r'^slett/dato/(?P<aktivitet_date>\d+)/$', 'delete_aktivitet_date'),
)
