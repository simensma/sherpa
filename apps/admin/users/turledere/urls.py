# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.turledere.views',
    url(r'^$', 'index'),
    url(r'^rediger/(?P<user>\d+)/$', 'edit'),
    url(r'^rediger/sertifikat/(?P<user>\d+)/$', 'edit_certificate'),
    url(r'^aktive-foreninger/(?P<user>\d+)/$', 'edit_active_associations'),
    url(r'^slett/(?P<turleder>\d+)/$', 'remove'),
    url(ur'^søk/$', 'search'),
)
