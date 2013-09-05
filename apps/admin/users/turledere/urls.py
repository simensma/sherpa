# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.turledere.views',
    url(r'^$', 'index'),
    url(r'^rediger/(?P<user>\d+)/$', 'edit'),
    url(ur'^søk/$', 'search'),
)
