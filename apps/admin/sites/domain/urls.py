# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.domain.views',

    url(r'^$', 'index'),

)
