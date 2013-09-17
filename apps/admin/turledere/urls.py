# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.turledere.views',
    url(r'^$', 'index'),
    url(r'^rediger/(?P<user>\d+)/$', 'edit'),
    url(r'^rediger/turledersertifikat/(?P<user>\d+)/$', 'edit_turleder_certificate'),
    url(r'^rediger/kursledersertifikat/(?P<user>\d+)/$', 'edit_kursleder_certificate'),
    url(r'^aktive-foreninger/(?P<user>\d+)/$', 'edit_active_associations'),
    url(r'^slett/turleder/(?P<turleder>\d+)/$', 'remove_turleder'),
    url(r'^slett/kursleder/(?P<kursleder>\d+)/$', 'remove_kursleder'),
    url(ur'^søk/$', 'search'),
)
