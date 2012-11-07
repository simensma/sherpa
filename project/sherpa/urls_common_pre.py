# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

# Common URL patterns for all sites to be applied first

urlpatterns = patterns('',
    url(r'^sherpa/', include('admin.urls', app_name='admin')),
    url(r'^minside/', include('user.urls')),
    url(ur'^søk/', 'page.views.search'),
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),
    url(r'^nyheter/', include('articles.urls')),
)
