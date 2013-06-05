# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.turledere.views',
    url(r'^$', 'index'),
    url(r'^rediger/(?P<profile>\d+)/$', 'edit'),
)
