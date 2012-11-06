# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',

    # Search
    url(ur'^søk/', 'page.views.search'),

    # Ads
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),

    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
