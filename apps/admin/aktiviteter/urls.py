# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/beskrivelse/(?P<aktivitet>\d+)/$', 'edit_description'),
    url(r'^rediger/pameldte/(?P<aktivitet>\d+)/$', 'edit_participants'),
    url(ur'^turledersøk/$', 'leader_search'),
    url(r'^turleder/legg-til/auto/$', 'leader_add_automatically'),
    url(r'^turleder/legg-til/manuelt/$', 'leader_add_manually'),
    url(r'^ny/dato/$', 'new_aktivitet_date'),
    url(r'^rediger/dato/(?P<aktivitet_date>\d+)/$', 'edit_aktivitet_date'),
    url(r'^slett/dato/(?P<aktivitet_date>\d+)/$', 'delete_aktivitet_date'),
)
