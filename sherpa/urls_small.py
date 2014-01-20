# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

handler403 = 'page.views.permission_denied'
handler404 = 'page.views.page_not_found'
handler500 = 'page.views.server_error'

urlpatterns = patterns('',

)
