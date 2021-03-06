# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('admin.turledere.views',
    url(r'^$', 'index'),
    url(r'^rediger/inaktiv/(?P<memberid>\d+)/$', 'edit_inactive'),
    url(r'^rediger/turledersertifikat/(?P<user>\d+)/$', 'edit_turleder_certificate'),
    url(r'^rediger/kursledersertifikat/(?P<user>\d+)/$', 'edit_kursleder_certificate'),
    url(r'^rediger/instruktorroller/(?P<user>\d+)/$', 'edit_instruktor_roles'),
    url(r'^aktive-foreninger/(?P<user>\d+)/$', 'edit_active_foreninger'),
    url(r'^slett/turleder/(?P<turleder>\d+)/$', 'remove_turleder'),
    url(r'^slett/kursleder/(?P<kursleder>\d+)/$', 'remove_kursleder'),
    url(ur'^søk/turledere/$', 'turleder_search'),
    url(ur'^søk/medlemmer/$', 'member_search'),
)
