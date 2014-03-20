# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.forening.views',
    url(r'^$', 'index', kwargs={'forening': None}),
    url(r'^rediger/(?P<forening>\d+)/$', 'index'),
)
