# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.analytics.views',
    url(r'^$', 'index'),
    url(ur'^søk/$', 'searches'),
)