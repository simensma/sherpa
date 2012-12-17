# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',
    url(r'^', include('sherpa.urls_common_pre')),

    url(r'^', include('sherpa.urls_common_post')),
)