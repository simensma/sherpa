# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.publications.views',

    url(r'^$', 'index'),
    url(r'^opprett/$', 'create'),
    url(r'^rediger/(?P<publication>\d+)/$', 'edit'),

)
