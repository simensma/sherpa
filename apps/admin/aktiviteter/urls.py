# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/beskrivelse/(?P<aktivitet>\d+)/$', 'edit_description'),
    url(r'^rediger/posisjon/(?P<aktivitet>\d+)/$', 'edit_position'),
    url(r'^rediger/pamelding/(?P<aktivitet>\d+)/$', 'edit_simple_signup'),
    url(r'^rediger/turdatoer/(?P<aktivitet>\d+)/$', 'edit_dates'),
    url(r'^rediger/turledere/(?P<aktivitet>\d+)/$', 'edit_leaders'),
    url(r'^rediger/pameldte/(?P<aktivitet>\d+)/$', 'edit_participants'),
    url(ur'^turledersøk/$', 'leader_search'),
    url(r'^turleder/legg-til/$', 'leader_assign'),
    url(r'^turleder/ta-bort/$', 'leader_remove'),
    url(r'^ny/dato/$', 'new_aktivitet_date'),
    url(r'^rediger/dato/(?P<aktivitet_date>\d+)/$', 'edit_aktivitet_date'),
    url(r'^slett/dato/(?P<aktivitet_date>\d+)/$', 'delete_aktivitet_date'),
)
