# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.sites.analytics.views',
    url(r'^$', 'index'),
    url(ur'^søk/$', 'searches'),
    url(ur'^404/$', 'not_found'),
)
