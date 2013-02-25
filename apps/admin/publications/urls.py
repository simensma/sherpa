# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.publications.views',

    url(r'^$', 'index'),
    url(r'^opprett/publikasjon/$', 'create_publication'),
    url(r'^rediger/publikasjon/(?P<publication>\d+)/$', 'edit_publication'),
    url(r'^rediger/utgivelse/(?P<publication>\d+)/$', 'edit_release', {'release': None}),
    url(r'^rediger/utgivelse/(?P<publication>\d+)/(?P<release>\d+)/$', 'edit_release'),

)
