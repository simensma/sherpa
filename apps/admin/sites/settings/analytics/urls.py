# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.settings.analytics.views',
    url(r'^$', 'index'),
    url(ur'^analytics-ua/$', 'analytics_ua'),
    url(ur'^søk/$', 'searches'),
    url(ur'^404/$', 'not_found'),
)
