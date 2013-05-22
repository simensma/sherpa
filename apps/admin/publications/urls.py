# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.publications.views',

    url(r'^$', 'index'),
    url(r'^opprett/publikasjon/$', 'edit_publication', {'publication': None}),
    url(r'^rediger/publikasjon/(?P<publication>\d+)/$', 'edit_publication'),
    url(r'^slett/publikasjon/(?P<publication>\d+)/$', 'delete_publication'),
    url(r'^rediger/utgivelse/(?P<publication>\d+)/$', 'edit_release', {'release': None}),
    url(r'^rediger/utgivelse/(?P<publication>\d+)/(?P<release>\d+)/$', 'edit_release'),
    url(r'^slett/utgivelse/(?P<release>\d+)/$', 'delete_release'),

)
