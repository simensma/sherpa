# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

# Common URL patterns for all sites to be applied first

urlpatterns = patterns('',
    url(ur'^søk/', 'page.views.search'),
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),
)
