# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),
    url(r'^rediger/(?P<aktivitet>\d+)/$', 'edit'),
    url(r'^rediger/turforslagsok/$', 'turforslag_search'),
    url(r'^forhandsvisning/(?P<aktivitet>\d+)/$', 'preview'),
    url(r'^reimporter/(?P<aktivitet>\d+)/$', 'trigger_import'),
    url(r'^rediger/dato/forhandsvisning/$', 'edit_date_preview'),
    url(r'^rediger/dato/slett/$', 'delete_date_preview'),
    url(r'^pameldte/(?P<aktivitet>\d+)/$', 'participants'),
    url(ur'^turledersøk/$', 'turleder_search'),
    url(r'^manglende/$', 'failed_imports'),
)
